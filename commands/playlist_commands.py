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
    """
    Command to display a list of all songs from a CSV playlist.
    Each song becomes a selectable option for playback.
    """

    def __init__(
        self,
        csv_path: str,
        computer: CustomComputer,
        main_menu_name: str,
        main_menu_options: dict[str, MenuCommand]
    ):
        """
        Initialize with a CSV path and UI context.

        Preconditions:
            - csv_path must be a valid .csv file path.
            - computer must be a CustomComputer instance.
            - main_menu_name must be a string.
            - main_menu_options must be a dict with string keys and MenuCommand values.
        """
        assert isinstance(csv_path, str) and csv_path.endswith(".csv"), "csv_path must point to a .csv file"
        assert isinstance(main_menu_name, str) and main_menu_name.strip(), "main_menu_name must be a non-empty string"
        assert isinstance(main_menu_options, dict), "main_menu_options must be a dictionary"
        self.csv_path = csv_path
        self.computer = computer
        self.main_menu_name = main_menu_name
        self.main_menu_options = main_menu_options

    def execute(self, context: "Map", player: "HumanPlayer") -> list[Message]:
        """
        Displays all songs as selectable options.

        Returns:
            list[Message]: Menu options for each song, plus a 'Back' button.
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_full_path = os.path.join(current_dir, self.csv_path)
        assert os.path.isfile(csv_full_path), f"CSV file does not exist at {csv_full_path}"

        with open(csv_full_path, 'r') as f:
            reader = csv.reader(f)
            songs = [row[0] for row in reader if row]  # Only song titles

        song_options: Dict[str, MenuCommand] = {
            "Back": BackToMainMenuCommand(self.computer, self.main_menu_name, self.main_menu_options)
        }
        for song in songs:
            song_options[song] = PlaySongCommand(selected_song=song)

        self.computer.set_menu_options(song_options)
        return self.computer.player_interacted(player)


# ============================================================
# NEW PLAYLIST COMMANDS
# ============================================================

class CreatePlaylistCommand(MenuCommand):
    """
    Command to create a new playlist CSV file in the resources/playlists directory.
    """

    def __init__(
        self,
        computer: CustomComputer,
        main_menu_name: str,
        main_menu_options: dict[str, MenuCommand],
        new_csv_name: str = "new_playlist.csv"
    ):
        """
        Parameters:
            computer (CustomComputer): The interface used for interaction.
            main_menu_name (str): Title of the main menu.
            main_menu_options (dict): Menu options to return to after creation.
            new_csv_name (str): Name of the new playlist CSV to create.
        """
        assert isinstance(new_csv_name, str) and new_csv_name.endswith(".csv"), "new_csv_name must end in .csv"
        self.computer = computer
        self.main_menu_name = main_menu_name
        self.main_menu_options = main_menu_options
        self.new_csv_name = new_csv_name

    def execute(self, context: "Map", player: "HumanPlayer") -> list[Message]:
        """
        Creates the playlist file and informs the player.

        Returns:
            list[Message]: Confirmation message + refreshed menu.
        """
        csv_full_path = os.path.join(BASE_DIR, "resources", "playlists", self.new_csv_name)

        with open(csv_full_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["title", "genre", "popularity", "userrating"])  # CSV Header

        messages: List[Message] = [ServerMessage(player, f"Playlist created: {self.new_csv_name}.")]
        self.computer.set_menu_options(self.main_menu_options)
        messages.extend(self.computer.player_interacted(player))
        return messages


class OpenPlaylistCommand(MenuCommand):
    """
    Command to display a submenu where players can create or open playlists.
    """

    def __init__(self, computer: CustomComputer, main_menu_name: str, main_menu_options: dict[str, MenuCommand]):
        """
        Initializes the command with UI context and fallback menu options.

        Preconditions:
            - All arguments must be non-null and valid types.
        """
        self.computer = computer
        self.main_menu_name = main_menu_name
        self.main_menu_options = main_menu_options

    def execute(self, context: "Map", player: "HumanPlayer") -> list[Message]:
        """
        Presents options to create a new playlist or view an existing one.

        Returns:
            list[Message]: Menu message with new options.
        """
        new_menu: Dict[str, MenuCommand] = {
            "Create Playlist": CreatePlaylistCommand(
                computer=self.computer,
                main_menu_name=self.main_menu_name,
                main_menu_options=self.main_menu_options
            ),
            "Open Existing": SeeSongCommand(
                csv_path=os.path.join(BASE_DIR, "resources", "playlists", "$ome $exy $ongs 4 U.csv"),
                computer=self.computer,
                main_menu_name=self.main_menu_name,
                main_menu_options=self.main_menu_options
            ),
            "Back": BackToMainMenuCommand(self.computer, self.main_menu_name, self.main_menu_options)
        }

        self.computer.set_menu_options(new_menu)
        return self.computer.player_interacted(player)


# ============================================================
# BACK COMMAND
# ============================================================

class BackToMainMenuCommand(MenuCommand):
    """
    Command that resets the computer menu to its original state.
    """

    def __init__(self, computer: CustomComputer, main_menu_name: str, main_menu_options: dict[str, MenuCommand]):
        """
        Initializes the command with the menu to revert to.

        Preconditions:
            - All arguments must be valid types and non-empty.
        """
        self.computer = computer
        self.main_menu_name = main_menu_name
        self.main_menu_options = main_menu_options

    def execute(self, context: "Map", player: "HumanPlayer") -> list[Message]:
        """
        Resets the CustomComputer to its main menu and displays it.

        Returns:
            list[Message]: MenuMessage with original options.
        """
        self.computer.set_menu_options(self.main_menu_options)
        return [MenuMessage(self.computer, player, self.main_menu_name, list(self.main_menu_options.keys()))]
