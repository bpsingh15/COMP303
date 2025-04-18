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
    def __init__(self, csv_path: str):
        self.csv_path = csv_path

    def execute(self, context, player) -> List[Message]:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        csv_full_path = os.path.join(project_root, self.csv_path)

        with open(csv_full_path, 'r') as f:
            reader = csv.reader(f)
            header = next(reader)
            songs = [row[0].strip() for row in reader if row]

        print("\nVote for a song:")
        for i, song in enumerate(songs):
            print(f"{i+1}. {song}")
        choice = input("Enter the number of the song you want to vote for: ")

        try:
            selected_song = songs[int(choice) - 1]
        except (ValueError, IndexError):
            return [ServerMessage(player, "Invalid choice. Try again.")]

        MusicManager.get_instance().cast_vote(selected_song)
        return [ServerMessage(player, f"You voted for '{selected_song}'")]

