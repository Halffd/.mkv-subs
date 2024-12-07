import os
import subprocess
import re
import sys
import json
import tkinter as tk
from tkinter import filedialog, simpledialog
from tkinter import ttk

patt = ""
src = ""
target = ""
delay = None
cc = 0
pos = 1
start = 0
pos2 = 1
sort = True
mx = 60
ns = []
vad = ""
offset = 0
FFMPEG_PATH = "ffmpeg"
FFS_PATH = "ffs"
DIRECTORY = os.getcwd()
source_files = []
srt_files = []
backup_dir = os.path.join(DIRECTORY, "Backup")
os.makedirs(backup_dir, exist_ok=True)
typ = "srt"
search = False
patt = ''
directories = [DIRECTORY]
mode = 0

def extract_number(filename, count=True, pattern=None, group_index=None):
    global patt, pos, pos2, cc, start, ns
    filename = filename.split("\\")[-1]
    result = ''
    if pattern is None:
        pattern = patt
    if group_index is None:
        group_index = pos
    if patt == "pos" and count:
        result = cc
    else:
        if patt == "pos":
            pattern = r"(\d+)"
    match = re.findall(pattern, filename)
    # Find all matches and capture groups
    if match:
        print(match, patt, pattern, len(match), filename, end="\n")
        if not sort:
            if start < 2:
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
            try:
                result = int(match[1])
            except:
                result = 0
    else:
        result = 0
    if filename.find("srt") != -1 and result != '':
        print(f"{filename}: {result}")
    if count:
        cc += 1
    if not sort:
        ns.append(result)
    return result
def select_source_file():
    global src
    src = filedialog.askopenfilename(title="Select Source File")
    src_entry.delete(0, tk.END)
    src_entry.insert(0, src)
def select_target_file():
    global target
    target = filedialog.askopenfilename(title="Select Target File")
    target_entry.delete(0, tk.END)
    target_entry.insert(0, target)
def select_dir():
    global directory
    directory = filedialog.askdirectory(title="Select Directory")
    dir_entry.delete(0, tk.END)
    dir_entry.insert(0, directory)
def select_source_directory():
    global src_path
    src_path = filedialog.askdirectory(title="Select Source Directory")
    src_entry.delete(0, tk.END)
    src_entry.insert(0, src_path)
def select_target_directory():
    global srt_path
    srt_path = filedialog.askdirectory(title="Select Target Directory")
    target_entry.delete(0, tk.END)
    target_entry.insert(0, srt_path)
def run_script():
    global patt, ns, sort, start, vad
    srt_files = []
    source_files = []
    target = target_entry.get()
    src = src_entry.get()
    directories[0] = dir_entry.get()
    offset = int(episode_offset_entry.get())
    mx = int(max_offset_entry.get())
    delay = float(delay_entry.get())
    patt = regex_entry.get()
    # Define the data to be written
    data = {
        "target": target,
        "src": src,
        "directory": directories[0],
        "offset": offset
    }
    # Write the data to a file
    with open('sync.json', 'w') as file:
        json.dump(data, file, indent=4)
    # patt = re.escape(patt)
    print(f"Regular expression pattern: {patt}")
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
    srt_files = list(set(srt_files))
    fn = []
    """for f in source_files:
        n = extract_number(f)
        if(n in fn):
            source_files.remove(f)
        else:
            fn.append(n)
    for f in srt_files:
        n = extract_number(f)
        if(n in fn):
            srt_files.remove(f)
        else:
            fn.append(n)"""
    if delay is not None and delay != 0:
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
                base_name += f'-{src}.{target}'

                # Create the subtitle file path based on the original full path
                subtitle_file_path = os.path.join(DIRECTORY, f"{base_name}.srt")
                subtitle_file_path.replace("\\", "/")
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
def update_radio():
    mode = selected_mode.get()
    if mode == 2:
        episode_offset_entry.grid_forget()
        episode_offset_label.grid_forget()
        delay_label.grid(row=5, column=0, padx=20, pady=20, sticky="e")
        delay_entry.grid(row=5, column=1, padx=20, pady=20, sticky="ew")
        #dir_entry.configure(background='black')
    else:
        delay_label.grid_forget()
        delay_label.grid_forget()
        episode_offset_label.grid(row=5, column=0, padx=20, pady=20, sticky="e")
        episode_offset_entry.grid(row=5, column=1, padx=20, pady=20, sticky="ew")

root = tk.Tk()
root.title("Subtitle Extractor")
root.geometry("800x600")

# Set the dark theme
root.configure(bg='#2c2c2c')
# Create the main frame with a dark theme
frame = tk.Frame(root, bg='#2c2c2c')
frame.grid(row=0, column=0, sticky="nsew")

# Create the widgets with a dark theme
regex_label = tk.Label(frame, text="Regex:", fg='white', bg='#2c2c2c', font=("Arial", 16))
regex_entry = tk.Entry(frame, fg='white', bg='#4c4c4c', font=("Arial", 16))

src_label = tk.Label(frame, text="Source:", fg='white', bg='#2c2c2c', font=("Arial", 16))
src_entry = tk.Entry(frame, fg='white', bg='#4c4c4c', font=("Arial", 16))
src_button = tk.Button(frame, text="Browse", command=select_source_file, fg='white', bg='#4c4c4c', font=("Arial", 16))
src_dir_button = tk.Button(frame, text="Directory", command=select_source_directory, fg='white', bg='#4c4c4c', font=("Arial", 16))

target_label = tk.Label(frame, text="Target:", fg='white', bg='#2c2c2c', font=("Arial", 16))
target_entry = tk.Entry(frame, fg='white', bg='#4c4c4c', font=("Arial", 16))
target_button = tk.Button(frame, text="Browse", command=select_target_file, fg='white', bg='#4c4c4c', font=("Arial", 16))
target_dir_button = tk.Button(frame, text="Directory", command=select_target_directory, fg='white', bg='#4c4c4c', font=("Arial", 16))

dir_label = tk.Label(frame, text="Diretory", fg='white', bg='#2c2c2c', font=("Arial", 16))
dir_entry = tk.Entry(frame, fg='white', bg='#4c4c4c', font=("Arial", 16))
dir_button = tk.Button(frame, text="Browse", command=select_dir, fg='white', bg='#4c4c4c', font=("Arial", 16))

max_offset_label = tk.Label(frame, text="Max Offset (seconds):", fg='white', bg='#2c2c2c', font=("Arial", 16))
max_offset_entry = tk.Entry(frame, fg='white', bg='#4c4c4c', font=("Arial", 16))

episode_offset_label = tk.Label(frame, text="Episode Offset (Target):", fg='white', bg='#2c2c2c', font=("Arial", 16))
episode_offset_entry = tk.Entry(frame, fg='white', bg='#4c4c4c', font=("Arial", 16))

delay_label = tk.Label(frame, text="Delay:", fg='white', bg='#2c2c2c', font=("Arial", 16))
delay_entry = tk.Entry(frame, fg='white', bg='#4c4c4c', font=("Arial", 16))

run_button = tk.Button(frame, text="Run", command=run_script, fg='white', bg='#4c4c4c', font=("Arial", 16))

# Set the dark theme
style = tk.ttk.Style()
style.theme_use('clam')

# Set the font size for the menu
style.configure("TMenubutton", background="#333", foreground="white", activebackground="#444", activeforeground="white", font=("Arial", 32))
style.configure("TMenuItem", background="#333", foreground="white", activebackground="#444", activeforeground="white", font=("Arial", 16))
style.configure("TButton", background="#333", foreground="white", activebackground="#444", activeforeground="white", font=("Arial", 16))
style.configure("TLabel", background="#333", foreground="white", font=("Arial", 16))
style.configure("TEntry", background="#444", foreground="white", insertcolor="white", font=("Arial", 16))
style.configure("TRadiobutton", background="#333", foreground="white", activebackground="#444", activeforeground="white", font=("Arial", 16))

# Create the main menu
menubar = tk.Menu(root, bg="#333", fg="white", activebackground="#444", activeforeground="white", font=("Arial", 16))
root.config(menu=menubar)

# File menu
file_menu = tk.Menu(menubar)
menubar.add_cascade(label="File", menu=file_menu, font=("Arial", 38))
file_menu.add_command(label="Select Source File", command=select_source_file, font=("Arial", 16))
file_menu.add_command(label="Select Target File", command=select_target_file, font=("Arial", 16))
file_menu.add_command(label="Select Source Directory", command=select_source_directory, font=("Arial", 16))
file_menu.add_command(label="Select Target Directory", command=select_target_directory, font=("Arial", 16))
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit, font=("Arial", 16))

# Options menu
options_menu = tk.Menu(menubar)
menubar.add_cascade(label="Options", menu=options_menu, font=("Arial", 38))
options_menu.add_command(label="Run Script", command=run_script, font=("Arial", 16))

# Variable to hold the selected search mode
selected_mode = tk.IntVar()
selected_mode.set(0)  # Set the default selection to 0 (Search Text)

# Create radio buttons for search mode selection
search_text_radio = tk.Radiobutton(root, text="Search Text", variable=selected_mode, value=0, background="#333", foreground="white", activebackground="#444", activeforeground="white", font=("Arial", 22), command=update_radio)
search_directories_radio = tk.Radiobutton(root, text="Search Directories", variable=selected_mode, value=1, background="#333", foreground="white", activebackground="#444", activeforeground="white", font=("Arial", 22), command=update_radio)
delay_mode_radio = tk.Radiobutton(root, text="Delay Mode", variable=selected_mode, value=2, background="#333", foreground="white", activebackground="#444", activeforeground="white", font=("Arial", 22), command=update_radio)

# Grid the widgets
# Grid the radio buttons with more spacing
ypos = 520
search_text_radio.place(x=20, y=ypos)
search_directories_radio.place(x=240, y=ypos)
delay_mode_radio.place(x=560, y=ypos)

src_label.grid(row=1, column=0, padx=20, pady=20, sticky="e")
src_entry.grid(row=1, column=1, padx=20, pady=20, sticky="ew")
src_button.grid(row=1, column=2, padx=20, pady=20)
src_dir_button.grid(row=1, column=3, padx=20, pady=20)

target_label.grid(row=2, column=0, padx=20, pady=20, sticky="e")
target_entry.grid(row=2, column=1, padx=20, pady=20, sticky="ew")
target_button.grid(row=2, column=2, padx=20, pady=20)
target_dir_button.grid(row=2, column=3, padx=20, pady=20)

dir_label.grid(row=3, column=0, padx=20, pady=20, sticky="e")
dir_entry.grid(row=3, column=1, padx=20, pady=20, sticky="ew")
dir_button.grid(row=3, column=2, padx=20, pady=20)

max_offset_label.grid(row=4, column=0, padx=20, pady=20, sticky="e")
max_offset_entry.grid(row=4, column=1, padx=20, pady=20, sticky="ew")

episode_offset_label.grid(row=5, column=0, padx=20, pady=20, sticky="e")
episode_offset_entry.grid(row=5, column=1, padx=20, pady=20, sticky="ew")

# Grid the widgets with more spacing
regex_label.grid(row=6, column=0, padx=20, pady=20, sticky="e")
regex_entry.grid(row=6, column=1, columnspan=2, padx=20, pady=20, sticky="ew")
run_button.grid(row=7, column=1, padx=20, pady=20)

with open('sync.json', 'r') as file:
    data = json.load(file)

if data:
    target_entry.insert(0, data['target'])
    src_entry.insert(0, data['src'])
    dir_entry.insert(0, data['directory'])
    episode_offset_entry.insert(0, data['offset'])
else:
    episode_offset_entry.insert(0, "0")
max_offset_entry.insert(0, "60")
delay_entry.insert(0, "0")
regex_entry.insert(0, r"(\d+)")

root.mainloop()