#!/home/yann/git/scripts/sortDownloads/venv/bin/python

import os
import shutil
import configparser
import sys
from tmdbv3api import TMDb, Movie, TV
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from guessit import guessit as parser
from sanitize_filename import sanitize
import argparse

version = '1.0.0'

# Set up TMDb API
config = configparser.ConfigParser()
config.read('config.ini')
tmdb = TMDb()
tmdb.api_key = config['API']['tmdb_api_key']
tmdb.language = 'en'

movie_api = Movie()
tv_api = TV()

video_file_extensions = ['mp4', 'mkv', 'avi']
audio_file_extensions = ['mp3', 'flac', 'alac', 'aac', 'aiff', 'wav']
subtitle_file_extensions = ['srt', 'sub', 'stl']

# Helper functions
def move_file(src, dest, dry_run=False, ask_conf=False):
    if dry_run:
        print(f"\nDRY RUN\n{src} -->\n{dest}")
    else:
        execute = True
        if ask_conf:
            confirm = input(f"\n{src} -->\n{dest}\n? (y/n): ").lower()
            if confirm != 'y':
                execute = False
        if execute:
            if not os.path.exists(os.path.dirname(dest)):
                os.makedirs(os.path.dirname(dest))
            shutil.move(src, dest)
            print(f"\n{src} ->\n{dest}")

def find_movie_info(title):
    search_result = movie_api.search(title)
    if search_result.results:
        return search_result.results[0]
    return None

def find_tvshow_info(title):
    search_result = tv_api.search(title)
    if search_result.results:
        return search_result.results[0]
    return None

def rename_and_move_movie(file_path, movie_title, movie_year, dest_folder, dry_run=False, ask_conf=False):
    file_name, file_ext = os.path.splitext(file_path)
    new_folder_name = f"{movie_title} ({movie_year})"
    new_folder_path = os.path.join(dest_folder, new_folder_name)
    new_file_name = f"{new_folder_name}{file_ext}"
    move_file(file_path, os.path.join(new_folder_path, new_file_name), dry_run, ask_conf)

def move_movie_subtitle(file_path, movie_title, movie_year, dest_folder, dry_run=False, ask_conf=False):
    new_folder_name = f"{movie_title} ({movie_year})"
    new_folder_path = os.path.join(dest_folder, new_folder_name)
    filename = os.path.basename(file_path)
    move_file(file_path, os.path.join(new_folder_path, filename), dry_run, ask_conf)

def rename_and_move_tvshow(file_path, show_title, season_num, episode_num, episode_name, dest_folder, dry_run=False, ask_conf=False):
    file_name, file_ext = os.path.splitext(file_path)
    season_folder = f"Season {int(season_num):02}"
    episode_file_name = f"S{int(season_num):02}E{int(episode_num):02} - {sanitize(episode_name)}{file_ext}"
    season_folder = os.path.join(dest_folder, sanitize(show_title), season_folder)
    move_file(file_path, os.path.join(season_folder, episode_file_name), dry_run, ask_conf)

def file_is_video(extension):
    return extension.lower() in video_file_extensions

def file_is_audio(extension):
    return extension.lower() in audio_file_extensions

def file_is_subtitle(extension):
    return extension.lower() in subtitle_file_extensions

def get_subtitles_movie(movie_path, src_folder, movie_title, movie_year, dest_folder, dry_run=False, ask_conf=False):
    folder = os.path.dirname(movie_path)
    while folder != src_folder:
        for root, dirs, files in os.walk(folder):
            for filename in files:
                file_path = os.path.join(root, filename)
                file_ext = filename.split('.')[-1].lower()
                if file_is_subtitle(file_ext):
                    move_movie_subtitle(file_path, movie_title, movie_year, dest_folder, dry_run, ask_conf)
        
        folder = os.path.dirname(folder)

def delete_files(files_to_delete, dry_run=False, ask_conf=False):
    for file in files_to_delete:
        if dry_run:
            print(f"\nDRY RUN\n{file} -->\nThrash")
        else:
            execute = True
            if ask_conf:
                confirm = input(f"\n{file} -->\nTrash ?\n(y/n): ").lower()
                if confirm != 'y':
                    execute = False
            if execute:
                try:
                    os.remove(file)
                    print(f"\n{file} -->\nThrash")
                except FileNotFoundError:
                    print(f"File not found: {file}")
                except PermissionError:
                    print(f"Permission denied: {file}")
                except Exception as e:
                    print(f"Error deleting file {file}: {e}")

def _remove_empty_folders(folder, dry_run=False, ask_conf=False):
    # Walk the directory tree from the bottom up (deepest subdirectories first)
    for dirpath, dirnames, filenames in os.walk(folder, topdown=False):
        # If the directory is empty (no files or subdirectories), remove it
        if not dirnames and not filenames and not dirpath == folder:
            if dry_run:
                print(f"\n{dirpath} -->\nThrash")
            else:
                execute = True
                if ask_conf:
                    confirm = input(f"{dirpath} -->\nThrash ?\n(y/n): ").lower()
                    if confirm != 'y':
                        execute = False
                if execute:
                    try:
                        os.rmdir(dirpath)
                        print(f"\n{dirpath} -->\nThrash")
                    except OSError as e:
                        print(f"Error removing folder {dirpath}: {e}")

def remove_empty_folders(folder, dry_run=False, ask_conf=False):
    # Execute twice as some empty folder could remain otherwise
    _remove_empty_folders(folder, dry_run, ask_conf)
    _remove_empty_folders(folder, dry_run, ask_conf)
    
# Main function to sort files
def sort_files(src_folder, movie_dest, tv_dest, dry_run=False, ask_conf=False):
    files_to_delete = []
    for root, _, files in os.walk(src_folder):
        for filename in files:
            file_path = os.path.join(root, filename)
            file_ext = filename.split('.')[-1].lower()

            if not file_is_video(file_ext) and not file_is_audio(file_ext) and not file_is_subtitle(file_ext):
                files_to_delete.append(file_path)
                continue
            
            if file_is_video(file_ext):
                try:
                    parsed = parser(filename)
                    parsed_title = parsed['title']
                    
                except:
                    print(f"Couldn't parse : {filename}")
                    continue

                
                if 'season' in parsed and 'episode' in parsed:
                    # Handle TV show episode
                    res = find_tvshow_info(parsed_title)
                    if not res:
                        print(f"\nNo result found for '{filename}', skipping\n")
                        continue
                    show_id = res['id']
                    show_title = res['original_name']
                    season = parsed['season']
                    episode = parsed['episode']
                    episode_title = tv_api.details(f"{show_id}/season/{season}/episode/{episode}")['name']
                    rename_and_move_tvshow(file_path, show_title, season, episode, episode_title, tv_dest, dry_run, ask_conf)
                    # TV shows subtitles are not handled as too painful
                    
                else:
                    # Handle movies
                    res = find_movie_info(parsed_title)
                    if not res:
                        print(f"\nNo result found for '{filename}', skipping\n")
                        continue
                    movie_title = res['title']
                    movie_year = res['release_date'].split('-')[0]
                    rename_and_move_movie(file_path, movie_title, movie_year, movie_dest, dry_run, ask_conf)
                    get_subtitles_movie(file_path, src_folder, movie_title, movie_year, movie_dest, dry_run, ask_conf)

            # TODO Treat audio files
    
    delete_files(files_to_delete, dry_run, ask_conf)
    remove_empty_folders(src_folder, dry_run, ask_conf)

if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='Search for media files in download folder and sort them out')
    argparser.add_argument('src', type=str, help='Input folder containing downloaded files')
    argparser.add_argument('movies_dest', type=str, help='Folder containing Movies library')
    argparser.add_argument('tv_dest', type=str, help='Folder containing TV Shows library')
    argparser.add_argument('-c', '--confirmation', action='store_true', default=False, help='Request confirmation from user for each file move or delete')
    argparser.add_argument('-d', '--dryrun', action='store_true', default=False, help='Dry run, only display what would have been moved and deleted')
    argparser.add_argument('-v', '--version', action='version', version=version)
    args = argparser.parse_args()

    source_folder = os.path.abspath(args.src)
    movies_folder = os.path.abspath(args.movies_dest)
    tv_shows_folder = os.path.abspath(args.tv_dest)

    dry_run = args.dryrun
    ask_conf = args.confirmation

    sort_files(source_folder, movies_folder, tv_shows_folder, dry_run=dry_run, ask_conf=ask_conf)
    sys.exit(0)
