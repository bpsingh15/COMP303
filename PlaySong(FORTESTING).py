




"""

class PlaySongCommand(MenuCommand):
    def __init__(self, csv_path: str = "resources/sound/tswift_songs.csv", selected_song: Optional[str] = None):
        self.csv_path = csv_path
        self.selected_song = selected_song

    def execute(self, context: "Map", player: "HumanPlayer") -> List[Message]:
        # Open csv file
        with open(self.csv_path, 'r') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header row
            rows = [row for row in reader if row]

        # Select song if choice given if not choose random
        if self.selected_song:
            selected_row = None
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

        # Build query as "song_title artist audio"
        query = f"{song_title} {artist} audio"
        videosSearch = VideosSearch(query, limit=5)
        result = videosSearch.result()
        
        
        result_dict = cast(Dict[str, Any], result)
        results = result_dict['result']
        
        if not results:
            raise ValueError("No videos found for the given query")
        
        chosen_video = results[0]  # first result
        
        # Cas chosen video to a dictionary
        chosen_video_dict = cast(Dict[str, Any], chosen_video)
        song_url = chosen_video_dict['link']

        # Use relative directory for sound files
        sound_dir = "resources/sound"
        os.makedirs(sound_dir, exist_ok=True)

        # Create filename with both the song title and artist
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

        
"""