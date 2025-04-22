#!/usr/bin/env python

import os, sys, datetime
import re
import shutil
import ffmpeg
import pysrt
import send2trash
import colorsys

alignment_map = {
    '1': '↙',  # Bottom Left
    '2': '↓',  # Bottom Center
    '3': '↘',  # Bottom Right
    '4': '←',  # Middle Left
    '5': '↔',  # Middle Center (Centered)
    '6': '→',  # Middle Right
    '7': '↖',  # Top Left
    '8': '↑',  # Top Center
    '9': '↗',  # Top Right
}
patterns = [
    re.compile(r'{\\an\d}|<\/?[^>]+>'),
    re.compile(r'\\an(\d+)'), #{.?\\.*?}'), 1
    re.compile(r'{=\w+}'),
    re.compile(r"m\s(-?\d+(\.\d+)?)\s(-?\d+(\.\d+)?)"),
    re.compile(r"{.?\\.*?}"), #4
    re.compile(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]'),
    re.compile(r'>m\s+\d+(?:\.\d+)?\s+\d+(?:\.\d+)?(?:\s+b\s+\d+(?:\.\d+)?){6,}|\{\\an\d\}'),
    re.compile(r'\{.*?\}'), #7
    re.compile(r'{=\w+=\w+}'),
    re.compile(r'(\d{1,4}:\d{1,4}:\d{1,4},\d{1,8})\s*-->\s*(\d{1,4}:\d{1,4}:\d{1,4},\d{1,8})'),
    re.compile(r'color="#([A-Fa-f0-9]{1,9})"'), #10
    re.compile(r'#([A-Fa-f0-9]{1,9})'), #11
    re.compile(r'<[^>]+>'),
    re.compile(r'\{[^}]*?\}')
]
import re

alignment_map = {
    '1': '↙', # Bottom Left
    '2': '↓', # Bottom Center
    '3': '↘', # Bottom Right
    '4': '←', # Middle Left
    '5': '↔', # Middle Center (Centered)
    '6': '→', # Middle Right
    '7': '↖', # Top Left
    '8': '↑', # Top Center
    '9': '↗', # Top Right
}

def check_arrows(text):
    arrows = list(alignment_map.values())
    for arrow in arrows:
        arrow = '{' + arrow + '}'
        if re.search(re.escape(arrow), text):
            return True
    return False
def extract(html_string):
    pattern = patterns[12]
    outside_tags = re.sub(pattern, '', html_string)
    return outside_tags.strip()
def change_color(hex_color):
    # Remove the hash and convert hex color to RGB
    hex_color = hex_color.lstrip('#')
    rgb_color = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    
    # Convert RGB to HLS (HSL)
    # Note: colorsys.rgb_to_hls returns (hue, lightness, saturation)
    hls_color = colorsys.rgb_to_hls(rgb_color[0] / 255, rgb_color[1] / 255, rgb_color[2] / 255)

    # Check if lightness is below 0.6 (60%)
    if hls_color[1] < 0.95:
        # Increase lightness to 0.9
        hls_color = (hls_color[0], 0.95, hls_color[2])  # Keep hue and saturation unchanged
        # Convert HLS back to RGB
        rgb_color = colorsys.hls_to_rgb(*hls_color)
        # Scale back to 0-255 range
        rgb_color = tuple(int(c * 255) for c in rgb_color)
    
    # Convert RGB back to hex
    modified_hex_color = '#{:02x}{:02x}{:02x}'.format(*rgb_color)
    
    return modified_hex_color
def extract_hex_color(string):
    hex_color = re.search(patterns[10], string)
    if hex_color:
        h = hex_color.group(0)
        r = re.search(patterns[11], h)
        if r:
            return r.group(0)[1:]
        else: 
            return None
    else:
        return None
def replace_text_color(string):
    hex_color = extract_hex_color(string)
    if hex_color:
        try:
            modified_hex_color = change_color(hex_color)
            # print(f' --- #{modified_hex_color}')
            replaced_string = re.sub(patterns[11], modified_hex_color, string)
            return replaced_string
        except ValueError:
            pass
    return string
def calculate_japanese_percentage(file_path):
    global patterns
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()

    japanese_pattern = patterns[5]
    japanese_chars = re.findall(japanese_pattern, text)
    print(japanese_chars)
    total_chars = len(text)
    japanese_chars_count = len(japanese_chars)
    if japanese_chars_count <= 0:
        return False

    japanese_percentage = (japanese_chars_count / total_chars) * 100
    print(f'{japanese_percentage} - {file}')
    return japanese_percentage > 5


def has_coordinates(subtitle_text):
    global patterns
    match = re.search(patterns[3], subtitle_text)
    match2 = False #re.search(patterns[4], subtitle_text)
    #print(match, bool(match))
    return bool(match) or bool(match2)
def remove_ass_drawings(text):
    # Regular expression pattern to match the ASS drawing commands and \anX tags
    global patterns

    # Remove the ASS drawing commands and \anX tags from the text
    cleaned_text = re.sub(patterns[6], '', text)

    return cleaned_text
def merge_singleline_subs(subs):
    merged_subs = []
    current_sub = None

    for sub in subs:
        if current_sub is None:
            current_sub = sub
        elif current_sub.strip() == sub.strip() and current_sub.end == sub.start:
            current_sub.end = sub.end
        else:
            merged_subs.append(current_sub)
            current_sub = sub

    if current_sub is not None:
        merged_subs.append(current_sub)

    return merged_subs
def remove_duplicates(text, sep):
    lines = text.split(sep)
    unique_lines = []
    for line in lines:
        if line not in unique_lines:
            unique_lines.append(line)
    cleaned_text = sep.join(unique_lines)
    return cleaned_text

def convert_to_srt(text):
    # Remove formatting instructions enclosed in curly braces
    global patterns
    cleaned_text = re.sub(patterns[7], '', text)

    # Split the cleaned text into lines
    lines = cleaned_text.split()

    # Create the SRT content
    srt_content = ""
    for i, line in enumerate(lines, start=1):
        srt_content += f"{i}\n{line}\n\n"

    return srt_content.strip()
def replace_alignment(match):
    try:
        code = str(match.group(1))
        if code in alignment_map:
            return alignment_map[code]
        return match.group(0)
    except:
        return ''
def clean_srt_file(file_path, log_file, cd):
    global patterns
    try:
        cleaned_subs = []
        filtered_subs = []
        if isinstance(log_file, str):
            log_file = open(log_file, 'w')

        subs = pysrt.open(file_path, encoding='utf-8')
        lt = ''
        for sub in subs:
            t = extract(sub.text)
            if lt != t and not has_coordinates(sub.text) and not re.search(patterns[8], sub.text):
                filtered_sub = pysrt.SubRipItem(
                    index=sub.index,
                    start=sub.start,
                    end=sub.end,
                    text=sub.text
                )
                filtered_subs.append(filtered_sub)
                lt = t
        #for i, sub in enumerate(subs):
        """
        for sub in cleaned_sub_file:  # Iterate in reverse order to safely delete subtitles
            if not has_coordinates(sub.text): # and not re.search(patterns[8], sub):
                filtered_subs.append(sub)
            else:
                tims = re.search(patterns[9], filtered_subs[-1])
                if tims:
                    if i > 2:
                        filtered_subs = filtered_subs[:-3]
                    elif i > 1:
                        filtered_subs = filtered_subs[:-2]
"""
        # Create a new SubRipFile object with the filtered subtitles
        #cleaned_sub_file = []
        cleaned_sub_file = pysrt.SubRipFile(filtered_subs)
        lines = []
        timings = []
        add = 0
        """for i, sub in enumerate(filtered_subs):  # Iterate in reverse order to safely delete subtitles
            # Delete subs line
            times = re.search(patterns[9], sub)
            if times:
                try:
                    start_time = times.group(1)
                    end_time = times.group(2)
                    if start_time == timings[-1][0] and end_time == timings[-1][1]:
                        add = 3
                        if lines[-1].isdigit():
                            del lines[-1]
                    timings.append([start_time, end_time])
                    # Do something with the start_time and end_time
                    print(f"Subtitle timing: {start_time} --> {end_time}")
                    cleaned_sub_file.extend(lines)
                    lines = []
                except IndexError:
                    print("Invalid time format in subtitle line:")
            else:
                print("No time information found in subtitle line:")"""
            # sub = re.sub(patterns[0], '', sub)
            #re.sub(patterns[1], '', sub)
            #match = re.search(patterns[1], sub)
        for sub in cleaned_sub_file:  # Iterate in reverse order to safely delete subtitles
            sub.text = patterns[1].sub(replace_alignment, sub.text)
            #if match:
                #sub = convert_to_srt(sub)
            sub.text = re.sub(patterns[2], '', sub.text)
            sub.text = replace_text_color(sub.text)
            """if add > 0:
                add -= 1
            else:
                lines.append(sub)
        if len(lines) > 0:
            cleaned_sub_file.extend(lines)"""
        parent_dir = cd
        base_name = os.path.basename(file_path)
        new_file_path = os.path.join(parent_dir, base_name)
        cleaned_sub_file.save(new_file_path, encoding='utf-8')#with open(new_file_path, 'w', encoding='utf-8') as file:
            #file.writelines(cleaned_sub_file)
        # Load the SRT file
        dup = False
        subs = pysrt.open(new_file_path, encoding='utf-8')
        for sub in subs:
            if not check_arrows(sub.text):
                sub.text = re.sub(patterns[13], lambda match: match.group()[3:-1] if '**-' in match.group() else '', sub.text)
        path = os.path.join(parent_dir, base_name.split(".")[0]+"-Clean"+".srt")
        subs.save(path, encoding="utf-8")
        subs = cleaned_sub_file
        unique_lines = set()
        unique_subs = []
        log_entry = f'Processed: {file_path}\n'
        log_entry += f'lines: {unique_lines} {cleaned_subs}\n'
        log_entry += f'Cleaned file: {new_file_path}\n\n'
        log_file.write(log_entry)
        print(log_entry.strip())
        print(f'Subtitles cleaned successfully. {unique_lines} Cleaned file: {new_file_path}')
    except Exception as e:
        log_entry = f'Error occurred while cleaning subtitles in file: {file_path}\n'
        log_entry += f'Error message: {str(e)}\n\n'
        log_file.write(log_entry)
        print(log_entry.strip())
        print(f'Error occurred while cleaning subtitles in file: {file_path}')
        print(f'Error message: {str(e)}')
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
def main():
    current_directory = os.getcwd()
    strings = ['bat', 'C:']
    my_path = os.getcwd()
    cb = False
    script_dir = r"S:\Code\.mkv-subs"
    if not all(s in current_directory for s in strings):
        source_files = [
            f"{script_dir}\\subs.py",
            f"{script_dir}\\quicksrt=-ass.bat",
            f"{script_dir}\\subsdelay.bat",
            f"{script_dir}\\quickdefault.bat",
        ]

        for file_path in source_files:
            try:
                subprocess.run(["copy", "/Y", file_path, "."], shell=True)
            except Exception as e:
                print(e, file_path)
    else:
        current_directory = input("Directory: ")
        if current_directory != '':
            my_path = current_directory
    for ff in os.listdir(my_path):
        if ff.endswith('.ass'):
            input_file = os.path.join(my_path, ff)
            output_file = os.path.join(my_path, ff[:-4] + '.srt')

            try:
                ffmpeg.input(input_file).output(output_file, y='-y').run()
                print(f"Converted {ff} to {output_file}")
                # send2trash.send2trash(input_file)
            except ffmpeg.Error as e:
                print(f"Error converting {ff}: {e.stderr}")
    only_files = [f for f in os.listdir(my_path) if os.path.isfile(os.path.join(my_path, f))]

    log_file_path = os.path.join(my_path, 'srt_log.txt')
    with open(log_file_path, 'w') as log_file:
        backup_dir = os.path.join(my_path, 'Srt_Backup')
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        for file_name in only_files:
            typ = 'srt'
            seconds = 0
            if len(sys.argv) > 1:
                seconds = float(sys.argv[1])
                if len(sys.argv) > 2:
                    typ = sys.argv[2]
            else:
                typ = 'srt'
                seconds = 0
            if file_name.lower().endswith(f'.{typ}'):
                file_path = os.path.join(my_path, file_name)
                jp = calculate_japanese_percentage(file_path)
                if not jp and len(sys.argv) == 1:
                    backup_path = os.path.join(backup_dir, file_name)
                    if os.path.exists(backup_path):
                        # Add a number to the file name
                        base_name, extension = os.path.splitext(backup_path)
                        counter = 1
                        while os.path.exists(backup_path):
                            numbered_file = f"{base_name}_{counter}{extension}"
                            backup_path = os.path.join(backup_dir, numbered_file)
                            counter += 1
                    shutil.move(file_path, backup_path)
                    print(f'{seconds} .{typ} - Original file moved to backup: {backup_path}')
                    print("The file meets the English character percentage threshold.")
                    try:
                        # Create a backup by moving the original file to the backup directory

                        # Check if 'seconds' argument is provided
                        # Clean the subtitle file and save the cleaned version with the same name as the original
                        clean_srt_file(backup_path, log_file, my_path)
                    except Exception as e:
                        log_entry = f'Error occurred while processing file: {file_path}\n'
                        log_entry += f'Error message: {str(e)}\n\n'
                        log_file.write(log_entry)
                        print(log_entry.strip())
                        print(f'Error occurred while processing file: {file_path}')
                        print(f'Error message: {str(e)}')
                elif not (seconds == 0 and len(sys.argv) == 1):
                    print("Delay.")
                    filename = os.path.splitext(file_name)[0]
                    delayed_srt_file = f'_{filename}_delayed.{typ}'
                    # Execute ffmpeg command
                    command = f'ffmpeg -itsoffset {seconds} -i "{backup_path}" -c copy "{delayed_srt_file}"'
                    os.system(command)
                    print(f'Command executed: {command}')
    print(f'Log file created: {log_file_path}')
def process(file, dest, dirr):
    file_path = file
    backup_dir = os.path.join(dirr, 'Srt_Backup')
    backup_path = os.path.join(backup_dir, file)
    if os.path.exists(dest):
        # Add a number to the file name
        base_name, extension = os.path.splitext(dest)
        counter = 1
        # while os.path.exists(dest):
        #     numbered_file = f"{base_name}_{counter}{extension}"
        #     dest = os.path.join(backup_dir, numbered_file)
        #     counter += 1
    #shutil.move(file_path, dest)
    log_file_path = os.path.join(dirr, 'srt_log.txt')
    try:
        # Create a backup by moving the original file to the backup directory

        # Check if 'seconds' argument is provided
        # Clean the subtitle file and save the cleaned version with the same name as the original
        clean_srt_file(file_path, log_file_path, dirr)
    except Exception as e:
        log_entry = f'Error occurred while processing file: {file_path}\n'
        log_entry += f'Error message: {str(e)}\n\n'
        log_file_path.write(log_entry)
        print(log_entry.strip())
        print(f'Error occurred while processing file: {file_path}')
        print(f'Error message: {str(e)}')


if __name__ == '__main__':
    main()
"""def main():
    my_path = os.getcwd()
    only_files = [f for f in os.listdir(my_path) if os.path.isfile(os.path.join(my_path, f))]

    log_file_path = os.path.join(my_path, 'srt_log.txt')
    with open(log_file_path, 'w') as log_file:
        backup_dir = os.path.join(my_path, 'Srt_Backup')
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        for file_name in only_files:
            if file_name.lower().endswith('.srt'):
                file_path = os.path.join(my_path, file_name)
                backup_path = os.path.join(backup_dir, file_name)
                if isEnglish(file_path):
                    print("The file meets the English character percentage threshold.")
                    try:
                        # Create a backup by moving the original file to the backup directory
                        shutil.move(file_path, backup_path)
                        print(f'Original file moved to backup: {backup_path}')

                        # Clean the subtitle file and save the cleaned version with the same name as the original
                        clean_srt_file(backup_path, log_file)
                    except Exception as e:
                        log_entry = f'Error occurred while processing file: {file_path}\n'
                        log_entry += f'Error message: {str(e)}\n\n'
                        log_file.write(log_entry)
                        print(log_entry.strip())
                        print(f'Error occurred while processing file: {file_path}')
                        print(f'Error message: {str(e)}')
                else:
                    print("The file does not meet the English character percentage threshold.")
    print(f'Log file created: {log_file_path}')

if __name__ == '__main__':
    main()"""
