import os
import csv
import random

from .music_manager import MusicManager
from ..custom_computer import CustomComputer
from ..imports import *

from typing import TYPE_CHECKING, Optional, Any, Dict, cast, List
if TYPE_CHECKING:
    from coord import Coord
    from maps.base import Map
    from tiles.base import MapObject
    from tiles.map_objects import *
    from Player import HumanPlayer


class VoteForSongCommand(MenuCommand):
    """
    Command that prompts the player to vote for a song from a list loaded from a CSV.
    The chosen song receives a vote, which is tracked via the MusicManager singleton.
    """

    def __init__(self, csv_path: str):
        """
        Initialize the command with the path to the CSV file.

        Parameters:
            csv_path (str): Relative path to the playlist CSV file.

        Preconditions:
            - csv_path must be a valid, readable .csv file path.
        """
        assert isinstance(csv_path, str) and csv_path.endswith(".csv"), "csv_path must be a valid .csv file"
        self.csv_path = csv_path

    def execute(self, context, player) -> List[Message]:
        """
        Execute the voting prompt: display a numbered list of songs,
        accept player input, cast the vote, and return a confirmation message.

        Parameters:
            context (Map): The current map context (not used in this method).
            player (HumanPlayer): The player casting the vote.

        Returns:
            List[Message]: A list containing a ServerMessage indicating the result.

        Preconditions:
            - The CSV file must exist and be formatted with song titles in the first column.
            - The player must be a valid HumanPlayer object.
        """
        assert player is not None, "player must not be None"

        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        csv_full_path = os.path.join(project_root, self.csv_path)
        assert os.path.isfile(csv_full_path), f"CSV file does not exist at {csv_full_path}"

        with open(csv_full_path, 'r') as f:
            reader = csv.reader(f)
            header = next(reader, None)  # Skip header row if present
            songs = [row[0].strip() for row in reader if row]

        if not songs:
            return [ServerMessage(player, "No songs available to vote for.")]

        print("\nVote for a song:")
        for i, song in enumerate(songs):
            print(f"{i+1}. {song}")

        choice = input("Enter the number of the song you want to vote for: ")

        try:
            selected_index = int(choice) - 1
            selected_song = songs[selected_index]
        except (ValueError, IndexError):
            return [ServerMessage(player, "Invalid choice. Try again.")]

        MusicManager.get_instance().cast_vote(selected_song)
        return [ServerMessage(player, f"You voted for '{selected_song}'")]
