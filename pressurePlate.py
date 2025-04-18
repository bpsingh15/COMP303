from .myhouse import *

class MusicPressurePlate(PressurePlate):
    """
    A custom PressurePlate that plays a random song from a CSV when a player steps on it.
    Downloads the song using YouTube search and yt_dlp if not already cached.
    """

    def __init__(self, stepping_text: str, csv_path: str = "resources/playlists/$ome $exy $ongs 4 U.csv") -> None:
        """
        Initializes the MusicPressurePlate.

        Parameters:
            stepping_text (str): The text shown when the player steps on the plate.
            csv_path (str): Path to the CSV file containing song data.

        Preconditions:
            - `stepping_text` must be a non-empty string.
            - `csv_path` must point to a valid CSV file with song metadata.
        """
        assert isinstance(stepping_text, str) and stepping_text.strip() != "", "stepping_text must be a non-empty string"
        assert isinstance(csv_path, str) and csv_path.endswith(".csv"), "csv_path must be a .csv file"

        super().__init__(stepping_text=stepping_text)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.csv_full_path = os.path.join(current_dir, csv_path)
        assert os.path.isfile(self.csv_full_path), f"CSV file does not exist at {self.csv_full_path}"

    def player_entered(self, player) -> List[Message]:
        """
        Called when a player steps on the pressure plate. Picks a random song, downloads it if needed,
        and plays it through the game's audio system.

        Parameters:
            player (HumanPlayer): The player who triggered the pressure plate.

        Returns:
            List[Message]: A list of messages including a sound message for the chosen song.

        Preconditions:
            - `player` must be a valid player object.
            - The CSV file at `self.csv_full_path` must be readable and properly formatted.
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))

        with open(self.csv_full_path, 'r') as f:
            reader = csv.reader(f)
            header = next(reader)  # Skip header row
            rows = [row for row in reader if row]

        assert len(rows) > 0, "CSV must contain at least one data row"
        assert all(len(row) >= 2 for row in rows), "Each CSV row must contain at least song title and artist"

        # Choose a random song row and extract song title and artist
        song_title, artist = random.choice(rows)[0:2]

        # Build the query as "song_title artist audio"
        query = f"{song_title} {artist} audio"

        # Search for videos using YouTubeSearch
        videos_search = VideosSearch(query, limit=5)
        result = videos_search.result()
        result_dict = cast(Dict[str, Any], result)
        results = result_dict['result']
        assert results, f"No results found for query: {query}"
        chosen_video = results[0]

        song_url = chosen_video['link']

        # Prepare the sound directory
        sound_dir = os.path.join(current_dir, "resources", "sound")
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

        sound_msg = SoundMessage(player, wav_filename)
        return super().player_entered(player) + [sound_msg]
