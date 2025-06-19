import os
import sys
import subprocess
import shutil
import re
import json
import io
import pymkv
from pathlib import Path
import subs

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

# Step 4: Update process_subs() to handle SUP/SRT
def process_subs(file, dest, cb=False, vid=None, dirr=None):
    global vid_dir
    # Handle SUP files
    if file.endswith('.sup'):
        srt_file = os.path.splitext(file)[0] + '.srt'
        try:
            # Use SubtitleEdit for OCR conversion
            subprocess.run([
                'subtitleedit', '/convert', file, 'subrip',
                '/output', srt_file
            ], check=True)
            file = srt_file  # Use the converted SRT file
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to convert SUP to SRT: {e}")
    # Existing code for non-SRT files (now handles ASS only)
    if not file.endswith('.srt'):
        temp_srt = os.path.splitext(file)[0] + '.srt'
        try:
            subprocess.run(['ffmpeg', '-y', '-i', file, temp_srt], check=True)
            file = temp_srt
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error converting to SRT: {e}")
    dirr = os.path.dirname(file)    # Generate a default video path if vid is None
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
    if vid is None:
        vid = os.path.join(vid_dir, os.path.basename(file))
    # Process the subtitle file
    try:
        subs.process(file, vid, vid_dir)
    except Exception as e:
        raise RuntimeError(f"Error processing subtitles: {e}")
    # If cb is True, copy the processed subtitle file to the video path
    if cb:
        try:
            shutil.copy(file, vid_dir)
        except Exception as e:
            raise RuntimeError(f"Error copying file to video path: {e}")

    return vid  # Optionally return the video path
def show_exception_and_exit(exc_type, exc_value, tb):
    import traceback
    traceback.print_exception(exc_type, exc_value, tb)
    input("Press Enter to exit.")
    sys.exit(-1)

sys.excepthook = show_exception_and_exit

def check_dependencies():
    """Check if required dependencies are installed."""
    missing_deps = []
    
    # Check mkvmerge
    try:
        subprocess.run(['mkvmerge', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        missing_deps.append('mkvmerge')
    
    # Check if libboost is installed (Linux only)
    if sys.platform.startswith('linux'):
        try:
            subprocess.run(['ldconfig', '-p'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output = subprocess.check_output(['ldconfig', '-p']).decode()
            if 'libboost_filesystem.so' not in output:
                missing_deps.append('libboost-filesystem')
        except subprocess.CalledProcessError:
            missing_deps.append('libboost-filesystem')
    
    if missing_deps:
        print("\nMissing dependencies detected:")
        if 'mkvmerge' in missing_deps:
            print("\nmkvmerge is not installed. Please install it:")
            if sys.platform.startswith('linux'):
                print("  Ubuntu/Debian: sudo apt-get install mkvtoolnix")
                print("  Arch Linux: sudo pacman -S mkvtoolnix")
            elif sys.platform == 'darwin':
                print("  macOS: brew install mkvtoolnix")
            else:
                print("  Download from: https://mkvtoolnix.download/")
                
        if 'libboost-filesystem' in missing_deps:
            print("\nlibboost-filesystem is not installed. Please install it:")
            print("  Ubuntu/Debian: sudo apt-get install libboost-filesystem")
            print("  Arch Linux: sudo pacman -S boost-libs")
        
        sys.exit(1)

def main():
    # Add dependency check at the start
    check_dependencies()
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '-1':
            current_directory = input("Directory: ")
        else:
            current_directory = sys.argv[1]
    else:
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
        file_type = input("File type: ") or 'ass'

    mkv_files = [f for f in os.listdir(current_directory) if f.endswith(".mkv")]

    ass = os.path.join(current_directory, 'ass')
    srts = os.path.join(current_directory, 'srt')
    sup_dir = os.path.join(current_directory, 'sup')  # New directory for SUP files
    
    os.makedirs(ass, exist_ok=True)
    os.makedirs(srts, exist_ok=True)
    os.makedirs(sup_dir, exist_ok=True)  # Create SUP directory
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
    
    # FIRST: Extract all subtitle tracks BEFORE any muxing
    subtitle_results = []
    for track in mkv.tracks:
        if track.track_type == 'subtitles' and file_type not in ['mp3', 'mkv']:
            res = process_subtitle_track(track, file_name, ass, srts, file_type, current_directory)
            if res:
                subtitle_results.append((res, track))
    
    # SECOND: Process audio track detection
    for track in mkv.tracks:
        if track.track_type == 'audio':
            if track.language in ['jpn', 'und']:
                jpn = track.track_id
            elif track.language == 'eng':
                mux = True
    
    # THIRD: Do the audio muxing (this modifies the file)
    if mux and jpn is not None:
        full_path = os.path.join(current_directory, file_name)
        mux_audio_with_mkvmerge(full_path, jpn)
    
    # FOURTH: Process the extracted subtitles (file is now modified)
    for res, track in subtitle_results:
        if file_type == 'srt':
            dest = os.path.join(srts, f"{file_name[:-4]}.{track.track_id}.{track.language}.srt")
        else:
            dest = res
        process_subs(res, dest, cb, None, current_directory)

# Step 3: Update process_subtitle_track() to handle PGS
def process_subtitle_track(track, file_name, ass, srts, file_type, current_directory):
    sup_dir = os.path.join(current_directory, 'sup')  # Path to SUP directory
    
    # Detect PGS subtitles
    is_pgs = track.track_codec.lower() in ['hdmv pgs', 's_hdmv/pgs', 'pgs', 'pgs']
    
    if is_pgs:
        # Extract to SUP directory
        file_type = 'sup'
        name = f"{file_name[:-4]}.{track.track_id}.{track.language}.{file_type}"
        res = os.path.join(sup_dir, name)
    elif track.track_codec == 'SubRip/SRT':
        file_type = 'srt'
        name = f"{file_name[:-4]}.{track.track_id}.{track.language}.{file_type}"
        res = os.path.join(srts, name)
    else:
        file_type = 'ass'
        name = f"{file_name[:-4]}.{track.track_id}.{track.language}.{file_type}"
        res = os.path.join(ass, name)

    try:
        # Extract the subtitle track
        subprocess.run([
            "mkvextract", "tracks", 
            os.path.join(current_directory, file_name), 
            f"{track.track_id}:{res}"
        ], check=True)
        print(f"Extracted track {track.track_id} to {res}")

        # Convert SUP to SRT
        if is_pgs:
            srt_path = os.path.join(srts, name.replace('.sup', '.srt'))
            try:
                # Convert using vobsub2srt
                subprocess.run(['vobsub2srt', res], check=True)
                
                # Move generated SRT to srt directory
                generated_srt = Path(res).with_suffix('.srt').name
                shutil.move(generated_srt, srt_path)
                print(f"Converted {res} to {srt_path}")
                return srt_path  # Return path to SRT file
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                print(f"Failed to convert SUP to SRT: {e}")
                return None
        return res
    except subprocess.CalledProcessError as e:
        print(f"Failed to extract track: {e}")
        return None
def mux_audio_with_mkvmerge(file_path, jpn_track_id):
    filename = f"{os.path.basename(file_path)}.2.mkv"
    output_path = os.path.join(os.path.dirname(file_path), filename)
    eng_track_id = jpn_track_id - 1 if jpn_track_id == 1 else jpn_track_id + 1
    command = [
        "mkvmerge", "-o", output_path,
        "--audio-tracks", str(jpn_track_id),
        "--default-track-flag", f"{jpn_track_id}:yes",
        "--default-track-flag", f"{eng_track_id}:no",
        file_path
    ]

    print("Running:", ' '.join(command))
    print("CWD:", os.getcwd())
    print("File exists:", os.path.isfile(file_path))
    try:
        result = subprocess.run(command, capture_output=True)
        if result.returncode == 0:
            os.remove(file_path)
            os.rename(output_path, file_path)
            print("Successfully muxed audio.")
        else:
            print("Failed to mux audio.")
            print("STDERR:", result.stderr.decode())
            print("STDOUT:", result.stdout.decode())
    except subprocess.CalledProcessError as e:
        print(f"Error during muxing: {e}")

if __name__ == "__main__":
    main()
