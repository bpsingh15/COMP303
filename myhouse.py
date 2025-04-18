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
        """
        Sort a list of songs and return the sorted list.

        Parameters:
            songs (List[List[str]]): A list of songs, where each song is a list of fields.

        Returns:
            List[List[str]]: Sorted list of songs.

        Preconditions:
            - Each song must be a list with at least 5 elements.
        """
        pass


class SortByGenreStrategy(MusicSortingStrategy):
    def sort_songs(self, songs: List[List[str]]) -> List[List[str]]:
        """
        Sort songs alphabetically by genre (column index 2).

        Preconditions:
            - Each song must have at least 3 columns.
        """
        for song in songs:
            assert len(song) > 2, "Each song must have a genre field at index 2"
        return sorted(songs, key=lambda x: x[2])


class SortByPopularityStrategy(MusicSortingStrategy):
    def sort_songs(self, songs: List[List[str]]) -> List[List[str]]:
        """
        Sort songs by popularity (column index 3) descending.

        Preconditions:
            - Each song must have a valid integer at index 3.
        """
        for song in songs:
            assert len(song) > 3 and song[3].isdigit(), "Each song must have a valid integer popularity value at index 3"
        return sorted(songs, key=lambda x: int(x[3]), reverse=True)


class SortByUserRatingStrategy(MusicSortingStrategy):
    def sort_songs(self, songs: List[List[str]]) -> List[List[str]]:
        """
        Sort songs by user rating (column index 4) descending.

        Preconditions:
            - Each song must have a valid float at index 4.
        """
        for song in songs:
            assert len(song) > 4, "Each song must have a user rating field at index 4"
            float(song[4])  # Will raise ValueError if not valid
        return sorted(songs, key=lambda x: float(x[4]), reverse=True)


class Playlist:
    """
    Represents a music playlist that loads and sorts songs from a CSV file.
    """
    def __init__(self, csv_path: str):
        """
        Parameters:
            csv_path (str): Relative path to the CSV file containing the playlist.
        """
        assert isinstance(csv_path, str) and csv_path.endswith(".csv"), "csv_path must be a .csv file"
        self.csv_path = csv_path

    def load_songs(self) -> List[List[str]]:
        """
        Load songs from the CSV file, skipping the header row if present.

        Returns:
            List[List[str]]: A list of songs, each represented as a list of fields.

        Preconditions:
            - File must exist at the given path.
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_full_path = os.path.join(current_dir, self.csv_path)
        assert os.path.isfile(csv_full_path), f"{csv_full_path} does not exist"
        with open(csv_full_path, 'r') as f:
            reader = csv.reader(f)
            songs = [row for row in reader if row]
        if songs and songs[0][0].lower() == "title":
            songs = songs[1:]
        return songs

    def sortPlaylist(self, strategy: MusicSortingStrategy) -> List[List[str]]:
        """
        Sort songs using the provided strategy.

        Parameters:
            strategy (MusicSortingStrategy): The sorting strategy to apply.

        Returns:
            List[List[str]]: Sorted list of songs.
        """
        assert isinstance(strategy, MusicSortingStrategy), "strategy must implement MusicSortingStrategy"
        songs = self.load_songs()
        return strategy.sort_songs(songs)


# ============================================================
# SORTING COMMANDS (Using the Strategy Pattern)
# ============================================================

class SortByGenreCommand(MenuCommand):
    """
    Command to sort a playlist by genre and display the results.
    """
    def __init__(self, csv_path: str, computer: CustomComputer, main_menu_name: str, main_menu_options: dict[str, MenuCommand]):
        self.csv_path = csv_path
        self.computer = computer
        self.main_menu_name = main_menu_name
        self.main_menu_options = main_menu_options

    def execute(self, context: "Map", player: "HumanPlayer") -> list[Message]:
        """
        Executes the sort by genre command and returns interaction messages.
        """
        playlist = Playlist(self.csv_path)
        sorted_songs = playlist.sortPlaylist(SortByGenreStrategy())
        return self._display_sorted_songs(sorted_songs, player)

    def _display_sorted_songs(self, songs: List[List[str]], player: "HumanPlayer") -> list[Message]:
        """
        Internal helper to show the sorted songs to the player.
        """
        song_options: Dict[str, MenuCommand] = {"Back": BackToMainMenuCommand(self.computer, self.main_menu_name, self.main_menu_options)}
        for row in songs:
            song_options[row[0]] = PlaySongCommand(selected_song=row[0])
        self.computer.set_menu_options(song_options)
        return self.computer.player_interacted(player)


class SortByPopularityCommand(MenuCommand):
    """
    Command to sort a playlist by popularity.
    """
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
    """
    Command to sort a playlist by user rating.
    """
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
    """
    A custom map representing Paul's music lounge with a computer for music commands.
    """
    MAIN_ENTRANCE = True

    def __init__(self) -> None:
        """
        Initializes the house with default layout, music terminal, and mini-game room doors.
        """
        super().__init__(
            name="Paul House",
            description="Interact with the computer to select a song to play!",
            size=(15, 15),
            entry_point=Coord(14, 7),
            background_tile_image='wood_planks',
        )

    def player_entered(self, player: "HumanPlayer") -> list[Message]:
        """
        Welcomes the player to the music lounge.

        Returns:
            list[Message]: A greeting message to the player.
        """
        return [ServerMessage(player, "Welcome to your Music Lounge! This is Paul's project that he did alone!")]

    def get_objects(self) -> list[tuple[MapObject, Coord]]:
        """
        Returns all the map objects in the room including doors and computers.

        Returns:
            list[tuple[MapObject, Coord]]: Placed objects with coordinates.
        """
        objects: list[tuple[MapObject, Coord]] = []
        objects.append((Door('int_entrance', linked_room="Trottier Town", is_main_entrance=True), Coord(14, 7)))
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
