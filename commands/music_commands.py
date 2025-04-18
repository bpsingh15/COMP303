import os
import csv
import random
import yt_dlp
from youtubesearchpython import VideosSearch

from typing import TYPE_CHECKING, Optional, Any, Dict, cast, List
if TYPE_CHECKING:
    from coord import Coord
    from maps.base import Map
    from tiles.base import MapObject
    from tiles.map_objects import *
    from Player import HumanPlayer

from ..imports import *

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ============================================================
# MUSIC COMMANDS
# ============================================================

class PlaySongCommand(MenuCommand):
    """
    Command to play a selected or random song from the CSV playlist.
    Downloads song audio if not already saved locally.
    """

    def __init__(self, csv_path: str = "../resources/playlists/$ome $exy $ongs 4 U.csv", selected_song: Optional[str] = None):
        """
        Initialize with an optional selected song and the path to the playlist CSV.

        Preconditions:
            - csv_path must point to a valid CSV file.
            - selected_song must be a string or None.
        """
        assert isinstance(csv_path, str) and csv_path.endswith(".csv"), "csv_path must be a .csv file"
        if selected_song:
            assert isinstance(selected_song, str), "selected_song must be a string"
        self.csv_path = csv_path
        self.selected_song = selected_song

    def execute(self, context: "Map", player: "HumanPlayer") -> list[Message]:
        """
        Execute the song selection and play the sound.

        Returns:
            list[Message]: Contains a SoundMessage for playback.
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_full_path = os.path.join(current_dir, self.csv_path)

        assert os.path.exists(csv_full_path), f"CSV path {csv_full_path} does not exist"

        with open(csv_full_path, 'r') as f:
            reader = csv.reader(f)
            header = next(reader)
            rows = [row for row in reader if row]

        assert rows, "No song data available in CSV"

        # Select the song
        if self.selected_song:
            selected_row = None
            for row in rows:
                if row[0].strip().lower() == self.selected_song.strip().lower():
                    selected_row = row
                    break
            if selected_row:
                song_title = selected_row[0].strip()
                artist = selected_row[1].strip()
            else:
                song_title, artist = random.choice(rows)[0:2]
        else:
            song_title, artist = random.choice(rows)[0:2]

        player.set_state("last_song", f"{song_title} - {artist}")

        # YouTube search and download
        query = f"{song_title} {artist} audio"
        videosSearch = VideosSearch(query, limit=5)
        result = videosSearch.result()
        results = cast(Dict[str, Any], result)['result']
        assert results, f"No results found for query: {query}"
        chosen_video = results[0]
        song_url = chosen_video['link']

        sound_dir = os.path.join(BASE_DIR, "resources", "sound")
        os.makedirs(sound_dir, exist_ok=True)

        wav_filename = f"{song_title} - {artist}.wav"
        wav_path = os.path.join(sound_dir, wav_filename)

        if not os.path.exists(wav_path):
            ydl_opts = {
                'format': 'bestaudio',
                'outtmpl': os.path.join(sound_dir, f"{song_title} - {artist}"),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'wav',
                    'preferredquality': '192'
                }],
                'ffmpeg_location': r'C:\ffmpeg\bin'
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([song_url])
        else:
            print(f"{wav_filename} already exists. Skipping download.")

        return [SoundMessage(player, wav_filename)]


class LastPlayedSongCommand(MenuCommand):
    """
    Command to display the last played song for the player.
    """

    def execute(self, context: "Map", player: "HumanPlayer") -> list[Message]:
        """
        Returns the last played song state message.

        Returns:
            list[Message]: A ServerMessage with last song info.
        """
        last_song = player.get_state("last_song")
        if last_song:
            return [ServerMessage(player, f"Last song you played: {last_song}")]
        else:
            return [ServerMessage(player, "You haven't played any songs yet!")]


class PauseSongCommand(MenuCommand):
    """
    Command to pause or unpause the currently playing song.
    """
    _paused = False

    def execute(self, context: "Map", player: "HumanPlayer") -> list[Message]:
        """
        Toggles between pausing and unpausing the song.
        """
        import pygame
        if PauseSongCommand._paused:
            pygame.mixer.music.unpause()
            PauseSongCommand._paused = False
            return [ServerMessage(player, "PauseSongCommand: Song unpaused!")]
        else:
            pygame.mixer.music.pause()
            PauseSongCommand._paused = True
            return [ServerMessage(player, "PauseSongCommand: Song paused!")]


class SkipSongCommand(MenuCommand):
    """
    Command to stop the currently playing song.
    """

    def execute(self, context: "Map", player: "HumanPlayer") -> list[Message]:
        """
        Immediately stops the song playback.
        """
        import pygame
        pygame.mixer.music.stop()
        return [ServerMessage(player, "SkipSongCommand: Song skipped!")]


class ShuffleSongCommand(MenuCommand):
    """
    Placeholder command to shuffle songs. Does not currently implement shuffling logic.
    """

    def execute(self, context: "Map", player: "HumanPlayer") -> list[Message]:
        return [ServerMessage(player, "ShuffleSongCommand: Shuffling songs!")]


class AddSongCommand(MenuCommand):
    """
    Command to allow users to add a new song entry to the playlist CSV.
    """

    def __init__(
        self,
        csv_path: str = "../resources/playlists/some_song_playlist.csv",
        prompt: str = ("Enter new song details in the following format:\n"
                       "title,artist,genre,popularity,userrating\n"
                       "Example: CN TOWER,Drake,Pop,100,4.5\n> ")
    ):
        """
        Initializes the command with a CSV path and input prompt.

        Preconditions:
            - csv_path must be a valid path to a CSV file.
        """
        assert isinstance(csv_path, str) and csv_path.endswith(".csv"), "csv_path must be a .csv file"
        self.csv_path = csv_path
        self.prompt = prompt

    def execute(self, context: "Map", player: "HumanPlayer") -> list[Message]:
        """
        Prompts user for song input and appends it to the playlist if valid.

        Returns:
            list[Message]: Confirmation or error message.
        """
        new_entry = input(self.prompt)
        fields = [field.strip() for field in new_entry.split(',')]

        if len(fields) != 5:
            return [ServerMessage(player, "Invalid input format. Please use: title,genre,popularity,userrating")]

        try:
            int(fields[3])  # popularity
            float(fields[4])  # userrating
        except ValueError:
            return [ServerMessage(player, "Invalid popularity or userrating value. Popularity must be an integer and userrating a float.")]

        csv_full_path = os.path.join(BASE_DIR, self.csv_path)

        with open(csv_full_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(fields)

        return [ServerMessage(player, f"Added song: {fields[0]}")]
