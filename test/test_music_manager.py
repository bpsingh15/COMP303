import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from multiplayer.music_manager import MusicManager, Observer


class DummyObserver(Observer):
    def __init__(self):
        self.last_data = {}

    def update(self, data):
        self.last_data = data

class TestMusicManager(unittest.TestCase):
    def setUp(self):
        # Reset singleton for each test
        MusicManager._instance = None  
        self.manager = MusicManager.get_instance()

    def test_singleton(self):
        other = MusicManager.get_instance()
        self.assertIs(self.manager, other)

    def test_cast_vote_and_counts(self):
        self.manager.cast_vote("Song A")
        self.assertEqual(self.manager.get_vote_counts()["Song A"], 1)
        # cast again
        self.manager.cast_vote("Song A")
        self.assertEqual(self.manager.get_vote_counts()["Song A"], 2)

    def test_observer_notification(self):
        obs = DummyObserver()
        self.manager.add_observer(obs)

        self.manager.cast_vote("Song B")

        # Ensure observer was notified and data is valid
        self.assertIsInstance(obs.last_data, dict)
        self.assertEqual(obs.last_data.get("type"), "vote")
        self.assertEqual(obs.last_data.get("song"), "Song B")
        self.assertEqual(obs.last_data.get("votes"), 1)

        # Cleanup
        self.manager.remove_observer(obs)


if __name__ == "__main__":
    unittest.main()
