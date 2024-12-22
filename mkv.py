import os
import sys
import subprocess
import shutil
import re
import json
import io
import pymkv

vid_dir = None
def convert_mp3_to_wav(mp3_path, wav_path):
    try:
        command = [
            'ffmpeg', '-i', mp3_path,
            '-ar', '16000', '-ac', '1', '-c:a', 'pcm_s16le', wav_path
        ]
        subprocess.run(command, check=True)
        print(f"Converted {mp3_path} to {wav_path}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to convert {mp3_path} to WAV: {e}")
def clean_filename(filename):
    # Remove brackets, parentheses, arrows, and everything inside them
    cleaned = re.sub(r'\[.*?\]|\(.*?\)|<.*?>|{.*?}', '', filename)
    # Remove extra spaces and trim the result
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def mkdir(directory_path):
    """Create a directory if it doesn't exist."""
    try:
        os.makedirs(directory_path, exist_ok=True)  # Creates the directory if it doesn't exist
        print(f"Directory '{directory_path}' is created or already exists.")
    except Exception as e:
        print(f"Error creating directory '{directory_path}': {e}")
def process_subs(file, dest, cb=False, vid=None, dirr=None):
    global vid_dir
    import subs  # Assuming subs.py has a function to process subtitles

    # Validate inputs
    if not isinstance(file, str) or not os.path.isfile(file):
        raise ValueError("The 'file' parameter must be a valid file path.")
    if not isinstance(dest, str):
        raise ValueError("The 'dest' parameter must be a valid destination path.")

    # Check if the file needs conversion to .srt
    if not file.endswith('.srt'):
        # Create a temporary SRT filename
        temp_srt = os.path.splitext(file)[0] + '.srt'
        try:
            # Use FFmpeg to convert the file to SRT
            subprocess.run(['ffmpeg', '-y', '-i', file, temp_srt], check=True)
            file = temp_srt  # Use the converted file for processing
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error converting file to .srt: {e}")
    dirr = os.path.dirname(file)
    # Process the subtitle file
    try:
        subs.process(file, dest, dirr)
    except Exception as e:
        raise RuntimeError(f"Error processing subtitles: {e}")

    # Generate a default video path if vid is None
    if vid_dir is None:
        home = os.path.expanduser('~')  # Get the home directory for both Windows and Linux
        
        # Get the directory name containing the file
        file_dir = os.path.dirname(file)  # Get the directory path
        directory_name = os.path.basename(file_dir)  # Extract the last part of the path
        if directory_name == 'ass' or directory_name == 'srt':
            file_dir = os.path.dirname(file_dir)  # Get the directory path
            directory_name = os.path.basename(file_dir)  # Extract the last part of the path
            
        # Get the parent directory
        parent_dir = os.path.dirname(file_dir)
        parent_directory_name = os.path.basename(parent_dir)

        # Check the length of the parent directory name
        if len(parent_directory_name) > 10:
            directory_name = parent_directory_name + '_' + directory_name  # Append if length > 10

        unsupported_path_symbols = r'[<>:"/\\|?*]'  # Define unsupported symbols
        filename = clean_filename(directory_name)
        filename = re.sub(unsupported_path_symbols, '', filename)
        vid_dir = os.path.join(home, 'Documents', 'Subs', filename)  # Set default video path
        mkdir(vid_dir)
        print(vid_dir)
    if vid is None:
        vid = os.path.join(vid_dir, os.path.basename(file))
    # If cb is True, copy the processed subtitle file to the video path
    if cb:
        try:
            shutil.copy(file, vid)
        except Exception as e:
            raise RuntimeError(f"Error copying file to video path: {e}")

    return vid  # Optionally return the video path
def show_exception_and_exit(exc_type, exc_value, tb):
    import traceback
    traceback.print_exception(exc_type, exc_value, tb)
    input("Press Enter to exit.")
    sys.exit(-1)

sys.excepthook = show_exception_and_exit

def main():
    current_directory = os.getcwd()
    file_type = "ass"
    log_to_json = True

    # Handle platform-specific paths
    source_files = [
        os.path.join("C:", "Users", "halff", "Documents", ".mkv-subs", "subs.py"),
        os.path.join("C:", "Users", "halff", "Documents", ".mkv-subs", "quicksrt=-ass.bat")
    ]

    cb = True
    # Check if the script is executed in the same directory as the script or one above
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if current_directory == script_dir or current_directory == os.path.dirname(script_dir):
        cb = False

    if any(s in current_directory for s in ['E:']):
        for file_path in source_files:
            try:
                shutil.copy(file_path, ".")
            except Exception as e:
                print(e, file_path)
    else:
        current_directory = input("Directory: ")
        file_type = input("File type: ") or 'ass'

    mkv_files = [f for f in os.listdir(current_directory) if f.endswith(".mkv")]

    ass = os.path.join(current_directory, 'ass')
    srts = os.path.join(current_directory, 'srt')

    os.makedirs(ass, exist_ok=True)
    os.makedirs(srts, exist_ok=True)

    for file_name in mkv_files:
        file_path = os.path.join(current_directory, file_name)
        mkv = pymkv.MKVFile(file_path)

        if log_to_json:
            json_path = os.path.join("log", f"info_{file_name}.json")
            os.makedirs(os.path.dirname(json_path), exist_ok=True)
            with open(json_path, "w") as log:
                json.dump([track.__dict__ for track in mkv.tracks], log, indent=2)

        process_tracks(mkv, file_name, current_directory, ass, srts, file_type, cb)

def process_tracks(mkv, file_name, current_directory, ass, srts, file_type, cb):
    jpn = None
    mux = False

    for track in mkv.tracks:
        if track.track_type == 'audio':
            if track.language in ['jpn', 'und']:
                jpn = track.track_id
            elif track.language == 'eng':
                mux = True
        
        if track.track_type == 'subtitles' and file_type not in ['mp3', 'mkv']:
            res = process_subtitle_track(track, file_name, ass, srts, file_type, current_directory)
            if res:
                # Call process_subs after extracting the subtitle
                dest = os.path.join(srts, f"{file_name[:-4]}.{track.track_id}.{track.language}.srt")
                process_subs(res, dest, cb, None, current_directory)

        if mux:
            mux_audio_with_mkvmerge(file_name, jpn)

def process_subtitle_track(track, file_name, ass, srts, file_type, current_directory):
    if track.track_codec == 'SubRip/SRT':
        file_type = 'srt'
    else:
        file_type = 'ass'

    name = f"{file_name[:-4]}.{track.track_id}.{track.language}.{file_type}"
    res = os.path.join(ass, name)

    try:
        command = ["mkvextract", "tracks", os.path.join(current_directory, file_name), f"{track.track_id}:{res}"]
        subprocess.run(command, check=True)
        print(f"Extracted track {track.track_id} to {res}")
        return res  # Return the path of the extracted subtitle
    except subprocess.CalledProcessError as e:
        print(f"Failed to extract track: {e}")
        return None  # Return None if extraction failed

def mux_audio_with_mkvmerge(file_path, jpn):
    op = f"{file_path}.2.mkv"
    command = [
        "mkvmerge", "-o", op, "--atracks", str(jpn), file_path
    ]
    print(file_path, command, end="\n")
    try:
        result = subprocess.run(command, capture_output=True)
        if result.returncode == 0:
            os.remove(file_path)
            os.rename(op, file_path)
            print("Successfully muxed audio.")
        else:
            print(f"Failed to mux audio: {result.stderr.decode()}")
    except subprocess.CalledProcessError as e:
        print(f"Error during muxing: {e}")

if __name__ == "__main__":
    main()
