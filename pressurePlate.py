from .myhouse import *

class MusicPressurePlate(PressurePlate):
    def __init__(self, stepping_text: str, csv_path: str = "resources/playlists/$ome $exy $ongs 4 U.csv") -> None:
        super().__init__(stepping_text=stepping_text)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.csv_full_path = os.path.join(current_dir, csv_path)
    
    def player_entered(self, player) -> List[Message]:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Open the CSV and skip the header row
        with open(self.csv_full_path, 'r') as f:
            reader = csv.reader(f)
            header = next(reader)  # Skip header row
            rows = [row for row in reader if row]
        
        # Choose a random song row and extract song title and artist
        song_title, artist = random.choice(rows)[0:2]
        
        # Build the query as "song_title artist audio"
        query = f"{song_title} {artist} audio"
        
        # Search for videos (limit the search to 5 and pick the first result)
        videos_search = VideosSearch(query, limit=5)
        result = videos_search.result()
        result_dict = cast(Dict[str, Any], result)
        results = result_dict['result']
        chosen_video = results[0]  # Always select the first result
        
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
