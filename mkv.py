import os
import time
import sys
import pymkv
import ffmpeg
import subprocess
import shutil
import re
import json
import io



def convert_mp3_to_wav(mp3_path, wav_path):
    try:
        command = [
            'ffmpeg', '-i', mp3_path,
            '-ar', '16000',  # Set the audio sample rate to 16000 Hz
            '-ac', '1',      # Set the number of audio channels to 1 (mono)
            '-c:a', 'pcm_s16le',  # Set the audio codec to PCM signed 16-bit little-endian
            wav_path
        ]
        subprocess.run(command, check=True)
        print(f"Converted {mp3_path} to {wav_path} using ffmpeg with specified parameters")
    except subprocess.CalledProcessError as e:
        print(f"Failed to convert {mp3_path} to WAV using ffmpeg: {e}")

def sub(file, dest, cb, vid, dirr):
    import subs  # Assuming subs.py has a main function defined
    print("==========")
    subs.process(file, dest, dirr)  # Assuming subs.py has a main function defined
    if cb is True:
        shutil.copy(dest, vid)


def show_exception_and_exit(exc_type, exc_value, tb):
    import traceback

    traceback.print_exception(exc_type, exc_value, tb)
    input("Press key to exit.")
    sys.exit(-1)


sys.excepthook = show_exception_and_exit
# Copy required files
# Iterate over MKV files
current_directory = os.getcwd()
# Set variables
file_type = "ass"
log = "nyes"

strings = ['E:']
source_files = [
    "C:\\Users\\halff\\OneDrive\\Documents\\.mkv-subs\\subs.py",
    "C:\\Users\\halff\\OneDrive\\Documents\\.mkv-subs\\quicksrt=-ass.bat"
]
cb = False
if all(s in current_directory for s in strings):
    for file_path in source_files:
        try:
            subprocess.run(["copy", "/Y", file_path, "."], shell=True)
        except Exception as e:
            print(e, file_path)
else:
    current_directory = input("Directory: ")
    file_type = input("File type: ")
    if file_type == '':
        file_type = 'ass'
    cb = True

print("==========")
mkv_files = [
    file_name
    for file_name in os.listdir(current_directory)
    if file_name.endswith(".mkv")
]
if cb is False:
    ass = os.getcwd()
    srts = os.getcwd()
else:
    ass = os.path.join(os.getcwd(), 'ass')
    srts = os.path.join(os.getcwd(), 'srt')
directory = None
for file_name in mkv_files:
    file_path = os.path.join(current_directory, file_name)
    print(f'"{file_path}"')

    mkv = pymkv.MKVFile(file_path)
    if log == "yes":
        # Extract track information using pymkv

        # Save track information to JSON file
        json_path = f"log/info_{file_name}.json"
        log = open(json_path, "a")
            # f.write(str(mkv.__dict__))
            # json.dump(mkvt, f, indent=2)
    # Extract specific track using pymkv
    eng = None
    tracks = mkv.get_track()
    print(tracks)
    mg = None
    md = os.path.join(current_directory, file_name)
    jpn = 1
    mux = False
    for obj in tracks:
        if isinstance(log, io.IOBase) and not log.closed:
            log.write('\n')
            json.dump(obj.__dict__, log)
        track = obj._track_id
        tn = ""
        tns = obj.track_name
        print(tns, type(tns))
        if type(tns) is str and obj._track_type == 'subtitles':
            tns = tns.split(' ')
            tns = tns[0]
            if tns == "Signs":
                continue
            tn = f".{tns.lower()}"
        name = f"{file_name[:-4]}.{track}{tn}.{file_type}"
        print(obj.track_type, obj.track_codec, name)
        if tns is not None:
            eng = obj.language == 'eng' and not "japanese" in tns.lower()
        if (obj._track_type == 'audio' and (obj.language == 'jpn' or obj.language == 'und')):
            jpn = track
        if (obj._track_type == 'audio' and (eng or tns is None)):
            mux = True
            #mkv.remove_track(track)
        if (file_type == 'mp3' or file_type == 'wav') and obj._track_type == 'audio' and not eng:
            try:
                outex = obj.extract('')
                cd = os.path.join(current_directory, 'mp3')
                os.makedirs(cd, exist_ok=True)
                destination = os.path.join(cd, name)
                shutil.move(outex, destination)
                wav_path = os.path.splitext(destination)[0] + '.wav'
                convert_mp3_to_wav(destination, wav_path)
                print(f"Converted {destination} to {wav_path}")
            except subprocess.CalledProcessError as e:
                print(f'Subprocess returned non-zero exit status {e.returncode}.')
                print(e.stderr)
                print(f'Output: {e.output.decode()}')
        elif obj._track_type == 'subtitles' and file_type != 'mp3' and file_type != 'mkv':
            if obj.track_codec == 'SubRip/SRT':
                file_type = 'srt'
            else:
                file_type = 'ass'
            # (track_id=int(track))
            print(obj.language, track)
            # Save track to a separate file
            output_file = ""
            lang = obj.language
            out = f"{file_name}_[{track}]_{lang}"
            outpath = os.path.join(os.getcwd(), out)
            outpath2 = os.path.join(os.getcwd(), f"{out}.{file_type}")
            res = os.path.join(ass, name)
            try:
                print(res)
                outex = obj.extract('')
                try:
                    shutil.move(outex, res)
                except Exception:
                    os.rename(outpath, res)
                    os.rename(outpath2, res)
                # Convert to SRT using ffmpeg
                srt = f"{name[:-4]}.srt"
                srt_file = os.path.join(srts, srt)
                print(res, srt_file, srts, end='\n')
                if file_type == 'ass':
                    ffmpeg.input(res).output(srt_file, y='-y').run()
                    if directory is None:
                        pattern = r"\[.*?\]\s?|\s?(?:Dual Audio|BDRip 10 bits|\d+p|x265|BD|10bit|Opus|\(|\)|EMBER|DD)"
                        cd = current_directory.split('\\')
                        cdr = ''
                        if cd[-2].find(':') != -1:
                            cdr = cd[-1]
                        else:
                            cdr = cd[-2] + ' ' + cd[-1]
                        match = re.sub(pattern, '', cdr)
                        if match:
                            nam = match
                        else:
                            nam = cdr
                        if nam:
                            # Get the operating system name`
                            current_os = os.name
                            # Determine the user's home directory based on the operating system
                            if current_os == 'posix':  # Unix-like systems (Linux, macOS)
                                user_directory = os.path.expanduser("~")
                            elif current_os == 'nt':  # Windows
                                user_directory = os.path.expandvars("%USERPROFILE%")
                            else:
                                user_directory = None
                            # Print the result
                            if user_directory:
                                print(f"Operating System: {current_os}")
                                print(f"User's Home Directory: {user_directory}")
                                directory = os.path.join(user_directory, 'Documents', 'Subs', nam.strip())
                                if not os.path.exists(directory):
                                    os.makedirs(directory, exist_ok=True)
                                    print(f"Directory '{directory}' created successfully!")

                                    for file_path in source_files:
                                        try:
                                            subprocess.run(["copy", "/Y", file_path, directory], shell=True)
                                        except Exception as e:
                                            print(e, file_path)
                    # shutil.copy
                    dest = os.path.join(directory, srt)
                    sub(srt_file, dest, cb, os.path.join(current_directory, name), directory)
            except subprocess.CalledProcessError as e:
                print(e.stderr.decode('utf-8'), e.output.decode())
            except Exception as er:
                print(er)
    try:
        if type(log) is not str:
            log.close()
    except Exception as e:  
        print(e)
    try:
        if file_type == 'mkv' or mux:
            op = f"{file_path}.2.mkv"
            command = [
                "C:\\Users\\halff\\OneDrive\\Documents\\.bat\\mkvmerge.exe",
                "-o", op,
                "--atracks", str(jpn),
                file_path
            ]
            print(command)
            result = subprocess.run(command, capture_output=True)
            if result.returncode == 0:
                print("Command executed successfully.")
                os.remove(file_path)
                os.rename(op, file_path)
            else:
                print("Command failed with non-zero exit status:", result.returncode)
                print("Error output:", result.stderr.decode())
    except subprocess.CalledProcessError as e:
        print(e.stderr.decode('utf-8'), e.output.decode(), end='\n')
    except Exception as e:
        print(e)
print("==========")
#if directory is not None:
    #subs = os.path.join(directory, 'subs.py')
    #shutil.copy(os.path.join(os.getcwd(), 'subs.py'), subs)
    #subprocess.call(['cmd.exe','/c','cd', directory, '&', 'py subs.py'])
print("Press Enter to continue...")
time.sleep(5)
sys.exit()
