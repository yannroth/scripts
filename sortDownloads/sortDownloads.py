import os
import shutil
import re
from tmdbv3api import TMDb, Movie, TV
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3

# Set up TMDb API
tmdb = TMDb()
tmdb.api_key = 'YOUR_TMDB_API_KEY'  # Replace with your TMDb API key
tmdb.language = 'en'

movie_api = Movie()
tv_api = TV()

# Helper functions
def move_file(src, dest, dry_run=False):
    if dry_run:
        print(f"{src} -> {dest}")
    else:
        if not os.path.exists(os.path.dirname(dest)):
            os.makedirs(os.path.dirname(dest))
        shutil.move(src, dest)

def find_movie_info(title):
    search_result = movie_api.search(title)
    if search_result:
        return search_result[0]
    return None

def find_tvshow_info(title):
    search_result = tv_api.search(title)
    if search_result:
        return search_result[0]
    return None

def rename_and_move_movie(file_path, movie_info, dest_folder, dry_run=False):
    file_name, file_ext = os.path.splitext(file_path)
    title = movie_info.title
    year = movie_info.release_date.split('-')[0]
    new_folder_name = f"{title} ({year})"
    new_folder_path = os.path.join(dest_folder, new_folder_name)
    new_file_name = f"{title} ({year}){file_ext}"
    move_file(file_path, os.path.join(new_folder_path, new_file_name), dry_run=dry_run)

def rename_and_move_tvshow(file_path, tv_info, season_num, episode_num, episode_name, dest_folder, dry_run=False):
    file_name, file_ext = os.path.splitext(file_path)
    show_name = tv_info.name
    season_folder = f"Season {int(season_num):02}"
    episode_file_name = f"S{int(season_num):02}E{int(episode_num):02} - {episode_name}{file_ext}"
    show_folder = os.path.join(dest_folder, show_name, season_folder)
    move_file(file_path, os.path.join(show_folder, episode_file_name), dry_run=dry_run)

def rename_and_move_music(file_path, artist, album, year, track_num, track_name, dest_folder, dry_run=False):
    file_name, file_ext = os.path.splitext(file_path)
    album_folder = f"{year} - {album}"
    song_file_name = f"{track_num:02} - {track_name}{file_ext}"
    music_folder = os.path.join(dest_folder, artist, album_folder)
    move_file(file_path, os.path.join(music_folder, song_file_name), dry_run=dry_run)

# Main function to sort files
def sort_files(src_folder, movie_dest, tv_dest, music_dest, dry_run=False):
    for root, dirs, files in os.walk(src_folder):
        for file_name in files:
            print(f"treating file {file_name}")
            file_path = os.path.join(root, file_name)
            file_ext = file_name.split('.')[-1].lower()
            
            # Handle movies (assuming they are in a folder)
            if file_ext in ['mp4', 'mkv', 'avi']:
                base_name = re.sub(r'\.\w+$', '', file_name)
                movie_info = find_movie_info(base_name)
                if movie_info:
                    rename_and_move_movie(file_path, movie_info, movie_dest, dry_run=dry_run)
                else:
                    print(f"Movie info not found for {file_name}")

            # Handle TV shows
            elif re.match(r'.*S\d{2}E\d{2}.*', file_name, re.IGNORECASE):
                show_name = re.split(r'S\d{2}E\d{2}', file_name, flags=re.IGNORECASE)[0].strip()
                season_episode = re.search(r'S(\d{2})E(\d{2})', file_name, re.IGNORECASE)
                season_num, episode_num = season_episode.groups()
                tv_info = find_tvshow_info(show_name)
                if tv_info:
                    episode_name = f"Episode {episode_num}"  # You can make it smarter by looking up episode names.
                    rename_and_move_tvshow(file_path, tv_info, season_num, episode_num, episode_name, tv_dest, dry_run=dry_run)
                else:
                    print(f"TV show info not found for {file_name}")
            
            # Handle music
            elif file_ext in ['mp3', 'flac', 'aac']:
                try:
                    audio = MP3(file_path, ID3=EasyID3)
                    artist = audio['artist'][0]
                    album = audio['album'][0]
                    track_num = int(audio['tracknumber'][0].split('/')[0])
                    track_name = audio['title'][0]
                    year = audio['date'][0][:4]
                    rename_and_move_music(file_path, artist, album, year, track_num, track_name, music_dest, dry_run=dry_run)
                except Exception as e:
                    print(f"Error processing music file {file_name}: {e}")

            # Handle subtitles for movies and TV shows
            elif file_ext in ['srt', 'sub']:
                lang = 'unknown'
                if '.en.' in file_name:
                    lang = 'English'
                elif '.fr.' in file_name:
                    lang = 'French'
                # Add more language detection if needed
                base_name = re.sub(r'\.\w+$', '', file_name)
                subtitle_name = f"{lang}.{file_ext}"
                move_file(file_path, os.path.join(os.path.dirname(file_path), subtitle_name), dry_run=dry_run)

if __name__ == '__main__':
    source_folder = '/home/Downloads/test_script'  # Folder with freshly downloaded files
    movies_folder = '/home/Downloads/test_movies'     # Destination folder for movies
    tv_shows_folder = '/home/Downloads/test_tv' # Destination folder for TV shows
    music_folder = '/home/Downloads/test_music'       # Destination folder for music

    dry_run = True  # Set to True for testing, False for actual file moves

    sort_files(source_folder, movies_folder, tv_shows_folder, music_folder, dry_run=dry_run)
