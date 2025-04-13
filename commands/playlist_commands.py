import os
import csv
import random

from .music_commands import *
from ..custom_computer import CustomComputer

from typing import TYPE_CHECKING, Optional, Any, Dict, cast, List
if TYPE_CHECKING:
    from coord import Coord
    from maps.base import Map
    from tiles.base import MapObject
    from tiles.map_objects import *
    from Player import HumanPlayer

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ============================================================
# SEE SONGS COMMAND 
# ============================================================
class SeeSongCommand(MenuCommand):
    """Shows all songs from CSV, one per line.
       Adds a 'Back' option to return to the main menu.
    """
    def __init__(
        self,
        csv_path: str,
        computer: CustomComputer,
        main_menu_name: str,
        main_menu_options: dict[str, MenuCommand]
    ):
        self.csv_path = csv_path
        self.computer = computer
        self.main_menu_name = main_menu_name
        self.main_menu_options = main_menu_options

    def execute(self, context: "Map", player: "HumanPlayer") -> list[Message]:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_full_path = os.path.join(current_dir, self.csv_path)
        with open(csv_full_path, 'r') as f:
            reader = csv.reader(f)
            # Extract only the song title (column index 0)
            songs = [row[0] for row in reader if row]
        song_options: Dict[str, MenuCommand] = {}
        song_options["Back"] = BackToMainMenuCommand(self.computer, self.main_menu_name, self.main_menu_options)
        for song in songs:
            song_options[song] = PlaySongCommand(selected_song=song)
        self.computer.set_menu_options(song_options)
        return self.computer.player_interacted(player)

# ============================================================
# NEW PLAYLIST COMMANDS
# ============================================================
class CreatePlaylistCommand(MenuCommand):
    """Creates a new CSV playlist file in the resources/playlists folder."""
    def __init__(self, computer: CustomComputer, main_menu_name: str, main_menu_options: dict[str, MenuCommand], new_csv_name: str = "new_playlist.csv"):
        self.computer = computer
        self.main_menu_name = main_menu_name
        self.main_menu_options = main_menu_options
        self.new_csv_name = new_csv_name

    def execute(self, context: "Map", player: "HumanPlayer") -> list[Message]:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_full_path = os.path.join(BASE_DIR,"resources", "playlists", self.new_csv_name)
        with open(csv_full_path, 'w', newline='') as f:
            writer = csv.writer(f)
            # Write header row: title, genre, popularity, userrating
            writer.writerow(["title", "genre", "popularity", "userrating"])
        messages: List[Message] = [ServerMessage(player, f"Playlist created: {self.new_csv_name}.")]
        self.computer.set_menu_options(self.main_menu_options)
        messages.extend(self.computer.player_interacted(player))
        return messages


class OpenPlaylistCommand(MenuCommand):
    """Opens a submenu with options to create a new playlist or open an existing one."""
    def __init__(self, computer: CustomComputer, main_menu_name: str, main_menu_options: dict[str, MenuCommand]):
        self.computer = computer
        self.main_menu_name = main_menu_name
        self.main_menu_options = main_menu_options

    def execute(self, context: "Map", player: "HumanPlayer") -> list[Message]:
        new_menu: Dict[str, MenuCommand] = {}
        new_menu["Create Playlist"] = CreatePlaylistCommand(
            computer=self.computer,
            main_menu_name=self.main_menu_name,
            main_menu_options=self.main_menu_options
        )
        new_menu["Open Existing"] = SeeSongCommand(
            csv_path=os.path.join(BASE_DIR,"resources", "playlists", "$ome $exy $ongs 4 U.csv"),
            computer=self.computer,
            main_menu_name=self.main_menu_name,
            main_menu_options=self.main_menu_options
        )
        new_menu["Back"] = BackToMainMenuCommand(self.computer, self.main_menu_name, self.main_menu_options)
        self.computer.set_menu_options(new_menu)
        return self.computer.player_interacted(player)
    

# ============================================================
# BACK COMMAND
# ============================================================
class BackToMainMenuCommand(MenuCommand):
    """Resets the computer to the original main menu."""
    def __init__(self, computer: CustomComputer, main_menu_name: str, main_menu_options: dict[str, MenuCommand]):
        self.computer = computer
        self.main_menu_name = main_menu_name
        self.main_menu_options = main_menu_options

    def execute(self, context: "Map", player: "HumanPlayer") -> list[Message]:
        self.computer.set_menu_options(self.main_menu_options)
        return [MenuMessage(self.computer, player, self.main_menu_name, list(self.main_menu_options.keys()))]
