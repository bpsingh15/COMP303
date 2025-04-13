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
    def __init__(self, csv_path: str = "../resources/playlists/$ome $exy $ongs 4 U.csv", selected_song: Optional[str] = None):
        self.csv_path = csv_path
        self.selected_song = selected_song

    def execute(self, context: "Map", player: "HumanPlayer") -> list[Message]:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_full_path = os.path.join(current_dir, self.csv_path)
        
        # Open the CSV and skip the header row
        with open(csv_full_path, 'r') as f:
            reader = csv.reader(f)
            header = next(reader)  # Skip header row
            rows = [row for row in reader if row]
        
        # Select the song row based on provided selected_song or pick one randomly
        if self.selected_song:
            selected_row = None
            # Attempt to find the row where the title matches the provided selected_song (case insensitive)
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
        # Build the query as "song_title artist audio"
        query = f"{song_title} {artist} audio"
        
        # Search for videos (limit the search to 5 and pick the first result)
        videosSearch = VideosSearch(query, limit=5)
        result = videosSearch.result()
        result_dict = cast(Dict[str, Any], result)
        results = result_dict['result']
        chosen_video = results[0]  # Always select the first result
        
        song_url = chosen_video['link']
        sound_dir = os.path.join(BASE_DIR, "resources", "sound")
        os.makedirs(sound_dir, exist_ok=True)
        
        # Create a filename that includes both the song title and artist
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
    def execute(self, context: "Map", player: "HumanPlayer") -> list[Message]:
        last_song = player.get_state("last_song")
        if last_song:
            return [ServerMessage(player, f"Last song you played: {last_song}")]
        else:
            return [ServerMessage(player, "You haven't played any songs yet!")]




class PauseSongCommand(MenuCommand):
    _paused = False
    def execute(self, context: "Map", player: "HumanPlayer") -> list[Message]:
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
    def execute(self, context: "Map", player: "HumanPlayer") -> list[Message]:
        import pygame
        pygame.mixer.music.stop()
        return [ServerMessage(player, "SkipSongCommand: Song skipped!")]


class ShuffleSongCommand(MenuCommand):
    def execute(self, context: "Map", player: "HumanPlayer") -> list[Message]:
        return [ServerMessage(player, "ShuffleSongCommand: Shuffling songs!")]


class AddSongCommand(MenuCommand):
    """Prompts the user to add a song in the format: title,genre,popularity,userrating."""
    def __init__(
        self,
        csv_path: str = "../resources/playlists/some_song_playlist.csv",
        prompt: str = ("Enter new song details in the following format:\n"
                       "title,artist,genre,popularity,userrating\n"
                       "Example: CN TOWER,Drake,Pop,100,4.5\n> ")
    ):
        self.csv_path = csv_path
        self.prompt = prompt

    def execute(self, context: "Map", player: "HumanPlayer") -> list[Message]:
        # Prompt the user for input
        new_entry = input(self.prompt)
        # Split the entry by commas and remove extra whitespace
        fields = [field.strip() for field in new_entry.split(',')]
        
        # Validate that we have exactly 5 fields
        if len(fields) != 5:
            return [ServerMessage(player, "Invalid input format. Please use: title,genre,popularity,userrating")]

        # Validate that 'popularity' is an integer and 'userrating' is a float
        try:
            int(fields[3])  # Popularity should be an integer
            float(fields[4])  # User rating should be a float
        except ValueError:
            return [ServerMessage(player, "Invalid popularity or userrating value. Popularity must be an integer and userrating a float.")]

        # Determine the full CSV file path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_full_path = os.path.join(BASE_DIR, self.csv_path)

        # Append the new song entry to the CSV file
        with open(csv_full_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(fields)

        return [ServerMessage(player, f"Added song: {fields[0]}")]