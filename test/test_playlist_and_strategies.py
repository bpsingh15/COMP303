import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest, csv, tempfile
from COMP303.myhouse import (  # <<-- absolute import via the package
    Playlist,
    SortByGenreStrategy,
    SortByPopularityStrategy,
    SortByUserRatingStrategy
)


class TestPlaylistAndStrategies(unittest.TestCase):
    def setUp(self):
        # Create a temp CSV file
        self.tmp = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.csv')
        writer = csv.writer(self.tmp)
        writer.writerow(["title", "genre", "popularity", "rating"])
        writer.writerow(["Song1", "Rock", "50", "4.2"])
        writer.writerow(["Song2", "Jazz", "75", "3.8"])
        writer.writerow(["Song3", "Rock", "30", "4.9"])
        self.tmp.flush()
        self.tmp_path = self.tmp.name

    def tearDown(self):
        os.unlink(self.tmp_path)

    def test_load_songs(self):
        playlist = Playlist(self.tmp_path)
        songs = playlist.load_songs()
        # should skip header
        titles = [row[0] for row in songs]
        self.assertListEqual(titles, ["Song1","Song2","Song3"])

    def test_sort_by_genre(self):
        playlist = Playlist(self.tmp_path)
        result = playlist.sortPlaylist(SortByGenreStrategy())
        # Jazz comes before Rock
        self.assertEqual(result[0][1], "Jazz")

    def test_sort_by_popularity(self):
        playlist = Playlist(self.tmp_path)
        result = playlist.sortPlaylist(SortByPopularityStrategy())
        # highest popularity 75 first
        self.assertEqual(result[0][2], "75")

    def test_sort_by_rating(self):
        playlist = Playlist(self.tmp_path)
        result = playlist.sortPlaylist(SortByUserRatingStrategy())
        # highest rating 4.9 first
        self.assertAlmostEqual(float(result[0][3]), 4.9)

if __name__ == "__main__":
    unittest.main()
