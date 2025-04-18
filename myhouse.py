import os
import csv
import random

from .commands.music_commands import *
from .commands.playlist_commands import *
from .custom_computer import *

try:
    import yt_dlp
except:
    print("yt_dlp not installed. Won't be able to download songs.")

try:

    from youtubesearchpython import VideosSearch
except:
    print("youtubesearchpython not installed. Won't be able to download songs.")

from .imports import *
from abc import ABC, abstractmethod  # For strategy interface
from typing import TYPE_CHECKING, Optional, Any, Dict, cast, List
if TYPE_CHECKING:
    from coord import Coord
    from maps.base import Map
    from tiles.base import MapObject
    from tiles.map_objects import *
    from Player import HumanPlayer
    from command import MenuCommand


# ============================================================
# STRATEGY PATTERN FOR MUSIC SORTING
# ============================================================

class MusicSortingStrategy(ABC):
    @abstractmethod
    def sort_songs(self, songs: List[List[str]]) -> List[List[str]]:
        """Sort a list of songs (each song is a list of fields) and return the sorted list."""
        pass

class SortByGenreStrategy(MusicSortingStrategy):
    def sort_songs(self, songs: List[List[str]]) -> List[List[str]]:
        # Sort songs alphabetically by genre (column index 1)
        return sorted(songs, key=lambda x: x[2])

class SortByPopularityStrategy(MusicSortingStrategy):
    def sort_songs(self, songs: List[List[str]]) -> List[List[str]]:
        # Sort songs by popularity (column index 2) numerically descending (highest to lowest)
        return sorted(songs, key=lambda x: int(x[3]), reverse=True)

class SortByUserRatingStrategy(MusicSortingStrategy):
    def sort_songs(self, songs: List[List[str]]) -> List[List[str]]:
        # Sort songs by user rating (column index 3) numerically descending (highest to lowest)
        return sorted(songs, key=lambda x: float(x[4]), reverse=True)

class Playlist:
    def __init__(self, csv_path: str):
        self.csv_path = csv_path

    def load_songs(self) -> List[List[str]]:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_full_path = os.path.join(current_dir, self.csv_path)
        with open(csv_full_path, 'r') as f:
            reader = csv.reader(f)
            songs = [row for row in reader if row]
        # Skip header row if present (assumes first cell is "title")
        if songs and songs[0][0].lower() == "title":
            songs = songs[1:]
        return songs

    def sortPlaylist(self, strategy: MusicSortingStrategy) -> List[List[str]]:
        songs = self.load_songs()
        return strategy.sort_songs(songs)





# ============================================================
# SORTING COMMANDS (Using the Strategy Pattern)
# ============================================================

class SortByGenreCommand(MenuCommand):
    def __init__(self, csv_path: str, computer: CustomComputer, main_menu_name: str, main_menu_options: dict[str, MenuCommand]):
        self.csv_path = csv_path
        self.computer = computer
        self.main_menu_name = main_menu_name
        self.main_menu_options = main_menu_options

    def execute(self, context: "Map", player: "HumanPlayer") -> list[Message]:
        playlist = Playlist(self.csv_path)
        sorted_songs = playlist.sortPlaylist(SortByGenreStrategy())
        return self._display_sorted_songs(sorted_songs, player)

    def _display_sorted_songs(self, songs: List[List[str]], player: "HumanPlayer") -> list[Message]:
        song_options: Dict[str, MenuCommand] = {"Back": BackToMainMenuCommand(self.computer, self.main_menu_name, self.main_menu_options)}
        for row in songs:
            # row[0] is the song title
            song_options[row[0]] = PlaySongCommand(selected_song=row[0])
        self.computer.set_menu_options(song_options)
        return self.computer.player_interacted(player)


class SortByPopularityCommand(MenuCommand):
    def __init__(self, csv_path: str, computer: CustomComputer, main_menu_name: str, main_menu_options: dict[str, MenuCommand]):
        self.csv_path = csv_path
        self.computer = computer
        self.main_menu_name = main_menu_name
        self.main_menu_options = main_menu_options

    def execute(self, context: "Map", player: "HumanPlayer") -> list[Message]:
        playlist = Playlist(self.csv_path)
        sorted_songs = playlist.sortPlaylist(SortByPopularityStrategy())
        return self._display_sorted_songs(sorted_songs, player)

    def _display_sorted_songs(self, songs: List[List[str]], player: "HumanPlayer") -> list[Message]:
        song_options: Dict[str, MenuCommand] = {"Back": BackToMainMenuCommand(self.computer, self.main_menu_name, self.main_menu_options)}
        for row in songs:
            song_options[row[0]] = PlaySongCommand(selected_song=row[0])
        self.computer.set_menu_options(song_options)
        return self.computer.player_interacted(player)


class SortByUserRatingCommand(MenuCommand):
    def __init__(self, csv_path: str, computer: CustomComputer, main_menu_name: str, main_menu_options: dict[str, MenuCommand]):
        self.csv_path = csv_path
        self.computer = computer
        self.main_menu_name = main_menu_name
        self.main_menu_options = main_menu_options

    def execute(self, context: "Map", player: "HumanPlayer") -> list[Message]:
        playlist = Playlist(self.csv_path)
        sorted_songs = playlist.sortPlaylist(SortByUserRatingStrategy())
        return self._display_sorted_songs(sorted_songs, player)

    def _display_sorted_songs(self, songs: List[List[str]], player: "HumanPlayer") -> list[Message]:
        song_options: Dict[str, MenuCommand] = {"Back": BackToMainMenuCommand(self.computer, self.main_menu_name, self.main_menu_options)}
        for row in songs:
            song_options[row[0]] = PlaySongCommand(selected_song=row[0])
        self.computer.set_menu_options(song_options)
        return self.computer.player_interacted(player)





# ============================================================
# MYHOUSE MAP
# ============================================================
class PaulHouse(Map):
    MAIN_ENTRANCE = True
    def __init__(self) -> None:
        super().__init__(
            name="Paul House",
            description="Interact with the computer to select a song to play!",
            size=(15, 15),
            entry_point=Coord(14, 7),
            background_tile_image='wood_planks',
        )

    def player_entered(self, player: "HumanPlayer") -> list[Message]:
        return [ServerMessage(player, "Welcome to your Music Lounge! This is Paul's project that he did alone!")]

    def get_objects(self) -> list[tuple[MapObject, Coord]]:
        objects: list[tuple[MapObject, Coord]] = []
        objects.append((Door('int_entrance', linked_room="Trottier Town", is_main_entrance=True), Coord(14, 7)))
        
         # Add door objects linking to sub-rooms inside the house.
        objects.append((Door('int_entrance', linked_room="MyHouse GuessSong"), Coord(3, 3)))
        objects.append((Door('int_entrance', linked_room="MyHouse Multiplayer"), Coord(7, 3)))


        computer = CustomComputer(
            image_name="computer",
            menu_name="Select an option",
            menu_options={}
        )
        main_menu_options: Dict[str, MenuCommand] = {} 
        main_menu_options["Play Song"] = PlaySongCommand()
        main_menu_options["Last Played Song"] = LastPlayedSongCommand()
        main_menu_options["Pause Song"] = PauseSongCommand()
        main_menu_options["Add Song"] = AddSongCommand(
            csv_path=os.path.join("resources", "playlists", "$ome $exy $ongs 4 U.csv")
        )
        main_menu_options["Open Playlist"] = OpenPlaylistCommand(
            computer=computer,
            main_menu_name="Select an option",
            main_menu_options=main_menu_options
        )
        main_menu_options["Sort by Genre"] = SortByGenreCommand(
            csv_path=os.path.join("resources", "playlists", "$ome $exy $ongs 4 U.csv"),
            computer=computer,
            main_menu_name="Select an option",
            main_menu_options=main_menu_options
        )
        main_menu_options["Sort by Popularity"] = SortByPopularityCommand(
            csv_path=os.path.join("resources", "playlists", "$ome $exy $ongs 4 U.csv"),
            computer=computer,
            main_menu_name="Select an option",
            main_menu_options=main_menu_options
        )
        main_menu_options["Sort by User Rating"] = SortByUserRatingCommand(
            csv_path=os.path.join("resources", "playlists", "$ome $exy $ongs 4 U.csv"),
            computer=computer,
            main_menu_name="Select an option",
            main_menu_options=main_menu_options
        )
        computer.set_menu_options(main_menu_options)
        objects.append((computer, Coord(10, 7)))
        return objects



