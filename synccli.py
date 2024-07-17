
import os
import subprocess
import re
import sys

patt = "" # input("Regex ( (\d+), jp([０-９])), count/num pos ) : ")
src = input("Source file (Timed sub / Sub directory / Search): ")
target = ""
delay = None

if src != "":
target = input("Target file (Untimed sub / Search sub) / Delay: ")
if target.isdigit():
delay = int(target)
target = None
cc = 0
pos = 1
start = 0
if patt == "":
patt = r"(\d+)"
if patt == "jp" or patt == "pos" or patt == "ja" or patt == "count" or patt == "num":
patt = "pos"
cc = pos
pos2 = 1
sort = True

def extract_number(filename, count=True, pattern=None, group_index=None):
    global patt, pos, pos2, cc, start
    filename = filename.split("\")[-1]
    if pattern is None:
        pattern = patt
    if group_index is None:
        group_index = pos
    if patt == "pos" and count:
        result = cc
    else:
        if patt == "pos":
            pattern = r"(\d)"
            match = re.findall(pattern, filename)
    # Find all matches and capture groups
    if match:
        print(match, patt, pattern, len(match), filename, end="\n")
        if start < 2 and not sort:
            if count:
    pos = input("Position (srt 1): ")
    else:
    pos2 = input("Position (mkv 1): ")
    start += 1
    if pos != "":
    pos = int(pos)
    if pos == "":
    pos = 1
    if pos2 != "":
    pos2 = int(pos2)
    if pos2 == "":
    pos2 = 1
    try:
    if count:
    result = int(match[pos])
    else:
    result = int(match[pos2])
    except:
    result = int(match[0])
    else:
    result = float("inf")
    if filename.find("srt") != -1:
    print(f"{filename}: {result}")
    if count:
    cc += 1
    return result

mx = input("Maximumoffst seconds (60)")
vad = ""
if mx == "":
mx = 60
else:
mx = int(mx)
if mx < 0:
vad = "--vad=auditok "
mx = 30
offset = input("Episodes Offset [Target] (0): ")
if offset == "":
offset = 0
else:
offset = int(offset)
strings = ["bat", "C:"]
FFMPEG_PATH = "ffmpeg"
FFS_PATH = "ffs"
if not all(s in os.getcwd() for s in strings):
source_files = [
"C:\Users\halff\OneDrive\Documents\.scriptbat\subs.py",
"C:\Users\halff\OneDrive\Documents\.scriptbat\quicksrt=-ass.bat",
"C:\Users\halff\OneDrive\Documents\.scriptbat\subsdelay.bat",
"C:\Users\halff\OneDrive\Documents\.scriptbat\quickdefault.bat",
]

for file_path in source_files:
    try:
        subprocess.run(["copy", "/Y", file_path, "."], shell=True)
    except Exception as e:
        print(e, file_path)
DIRECTORY = os.getcwd()
else:
DIRECTORY = input("Directory: ")
cb = True

print(f"FFMPEG_PATH: {FFMPEG_PATH}")
print(f"FFS_PATH: {FFS_PATH}")
print(f"DIRECTORY: {DIRECTORY}")

source_files = []
srt_files = []
backup_dir = os.path.join(DIRECTORY, "Backup")
os.makedirs(backup_dir, exist_ok=True)

typ = "srt"
search = False # mkv: false
directories = [DIRECTORY] # Replace DIRECTORY1 with your desired directory path

if os.path.isdir(src):
search = True
directories.append(src)
elif target == "" or src == "":
search = True
                    
srt_files = []
source_files = []

for i, directory in enumerate(directories):
    for file in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, file)):
            if target:
                target_parts = target.split("/")
                target_match = all(
                    part.lower() in file.lower() for part in target_parts
                )

                if (target == "" and file.endswith(typ)) or (
                    file.endswith(typ) and target_match
                ):
                    srt_files.append(os.path.join(directory, file))

            src_parts = src.split("/")
            src_match = all(part.lower() in file.lower() for part in src_parts)
            if ((search or src == "\\") and file.endswith(".mkv")) or (
                not search and file.endswith(typ) and src_match
            ):
                source_files.append(os.path.join(directory, file))
source_files = list(set(source_files))
if delay is not None:
    print("Delay.")
    for file_name in source_files:
        filename = file_name.split("\\")[-1]
        dirc = "\\".join(file_name.split("\\")[0:-1])
        delayed_srt_file = f"{dirc}\\_{filename}_delayed.{typ}"
        print(f"{dirc}  -  {delayed_srt_file}")
        # Execute ffmpeg command
        command = (
            f'ffmpeg -itsoffset {delay} -i "{file_name}" -c copy "{delayed_srt_file}"'
        )
        os.system(command)
        print(f"Command executed: {command}")
    sys.exit(0)
srt_files = list(set(srt_files))
srt_files.sort(key=extract_number)
source_files.sort(key=extract_number)
if patt == "pos":
    cc = pos
c = pos
sort = False
print(f"{len(srt_files)} + {len(source_files)} {source_files}")
for srt_file in srt_files:
    srt_count = extract_number(srt_file)
    srt_count += offset
    # continue
    print(f"SRT file: {srt_file[-32:]}:  \n ___{srt_count}____")

    for mkv_file in source_files:
        # if patt == 'pos': mkv_count = c else:
        mkv_count = extract_number(mkv_file, False)
        print(mkv_count)
        if mkv_count == srt_count:
            mkv_file_path = os.path.join(DIRECTORY, mkv_file)
            print(f"Matching MKV file found: {mkv_file_path}")

            mkv_file_path = os.path.join(DIRECTORY, mkv_file)
            print(f"Running FFS for {mkv_file_path}")

            # Extract the base file name without the extension
            base_name = os.path.splitext(mkv_file)[0]

            # Create the subtitle file path based on the original full path
            subtitle_file_path = os.path.join(DIRECTORY, f"{base_name}.srt")
            print(
                FFS_PATH,
                mkv_file_path,
                "-i",
                srt_file,
                "-o",
                f"{subtitle_file_path}_sync.srt",
                "",
            )
            subprocess.run(
                [
                    FFS_PATH,
                    mkv_file_path,
                    "-i",
                    srt_file,
                    "-o",
                    f"{subtitle_file_path}-Sync.srt",
                    "--no-fix-framerate",
                    f"{vad}--max-offset-seconds={mx}",
                    "--gss",
                ]
            )
            break
    if offset != 0:
        srt_filename = os.path.basename(srt_file)

        # Check if the file name starts with a number
        if srt_filename[0].isdigit():
            # Extract the number from the file name
            num_match = re.match(r"\d+", srt_filename)
            if num_match:
                old_num = int(num_match.group())
                new_num = old_num + offset
                new_srt_filename = f"{new_num}:{srt_filename[len(str(old_num))+1:]}"
            else:
                new_srt_filename = f"{srt_count}:{srt_filename}"
        else:
            new_srt_filename = f"{srt_count}:{srt_filename}"

        new_srt_path = os.path.join(os.path.dirname(srt_file), new_srt_filename)

        # Check if the new file already exists
        if os.path.exists(new_srt_path):
            print(f"File already exists: {new_srt_path}")
             # Skip this file and move on to the next one

        try:
            os.rename(srt_file, new_srt_path)
        except OSError as e:
            print(f"Error renaming file: {srt_file} -> {new_srt_path}")
            print(e)
    else:
        print(f"Could not extract number from file path: {srt_file}")

input("Press Enter to exit...")
