import os, sys, datetime
import re
import shutil
import ffmpeg
import pysrt

def calculate_japanese_percentage(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()

    japanese_pattern = r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]'
    japanese_chars = re.findall(japanese_pattern, text)
    print(japanese_chars)
    total_chars = len(text)
    japanese_chars_count = len(japanese_chars)

    japanese_percentage = (japanese_chars_count / total_chars) * 100
    print(f'{japanese_percentage} - {file}')
    return japanese_percentage > 5

# ffmpeg -itsoffset 2 -i subtitles.srt -c copy subtitles_delayed.srt
def has_coordinates(subtitle_text):
    pattern = r"m\s(-?\d+(\.\d+)?)\s(-?\d+(\.\d+)?)"
    #pattern2 = r"\(?(\w)?{\*\\c&([A-Z][0-9])?\w+&}\.?\w?\s?"
    pattern2 = r"{.?\\.*?}"
    match = re.search(pattern, subtitle_text)
    match2 = re.search(pattern2, subtitle_text)
    print(match, bool(match))
    return bool(match) or bool(match2)
def isEnglish(srt_file_path, english_threshold=20):
    return True
    total_chars = 0
    english_chars = 0

    with open(srt_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line.isdigit():
                # Skip subtitle number
                continue
            if line:
                # Count English characters
                english_chars += sum(1 for char in line if 65 <= ord(char) <= 90 or 97 <= ord(char) <= 122)
                # Count total characters
                total_chars += len(line)

    english_percentage = (english_chars / total_chars) * 100 if total_chars > 0 else 0
    print(english_percentage,english_threshold,english_chars)
    return english_percentage >= english_threshold
def remove_ass_drawings(text):
    # Regular expression pattern to match the ASS drawing commands and \anX tags
    pattern = r'>m\s+\d+(?:\.\d+)?\s+\d+(?:\.\d+)?(?:\s+b\s+\d+(?:\.\d+)?){6,}|\{\\an\d\}'

    # Remove the ASS drawing commands and \anX tags from the text
    cleaned_text = re.sub(pattern, '', text)

    return cleaned_text
def merge_singleline_subs(subs):
    merged_subs = []
    current_sub = None

    for sub in subs:
        if current_sub is None:
            current_sub = sub
        elif current_sub.text.strip() == sub.text.strip() and current_sub.end == sub.start:
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
    cleaned_text = re.sub(r'\{.*?\}', '', text)

    # Split the cleaned text into lines
    lines = cleaned_text.split()

    # Create the SRT content
    srt_content = ""
    for i, line in enumerate(lines, start=1):
        srt_content += f"{i}\n{line}\n\n"

    return srt_content.strip()

def clean_srt_file(file_path, log_file, cd):
    try:
        pattern = r'>m\s+\d+(?:\.\d+)?\s+\d+(?:\.\d+)?(?:\s+b\s+\d+(?:\.\d+)?){6,}'
        cleaned_subs = []
        merged_text = None
        prev_sub = None
        subs = pysrt.open(file_path, encoding='utf-8')
        pattern_match = r'{=\w+=\w+}'
        filtered_subs = []
        if isinstance(log_file, str):
            log_file = open(log_file, 'w')

        for sub in subs:
            if not has_coordinates(sub.text) and not re.search(pattern_match, sub.text):
                filtered_sub = pysrt.SubRipItem(
                    index=sub.index,
                    start=sub.start,
                    end=sub.end,
                    text=sub.text
                )
                filtered_subs.append(filtered_sub)

        # Create a new SubRipFile object with the filtered subtitles
        cleaned_sub_file = pysrt.SubRipFile(filtered_subs)
        pattern = r'{.?\\.*?}'

        for sub in cleaned_sub_file:  # Iterate in reverse order to safely delete subtitles
            #Delete subs line
            sub.text = re.sub(r'({\\an\d}|<\/?[^>]+>)', '', sub.text)
            sub.text = re.sub(pattern, '', sub.text)
            match = re.search(pattern, sub.text)
            if match:
                sub.text = convert_to_srt(sub.text)
            sub.text = re.sub(r'{=\w+}', '', sub.text)
            '''if prev_sub is not None and sub.start == prev_sub.start and sub.end == prev_sub.end:
                # Merge duplicate lines
                if merged_text is None:
                    merged_text = prev_sub.text
                merged_text += ' ' + sub.text.replace('\n', ' ')
                merged_end = sub.end
            else:
                if merged_text is not None:
                    # Append the merged line to cleaned_subs
                    cleaned_subs.append(pysrt.SubRipItem(start=prev_sub.start, end=merged_end, text=merged_text))
                    merged_text = None
                cleaned_subs.append(sub)
            # Merge single-line subtitles
            prev_sub = sub

        if merged_text is not None:
            # Append the last merged line to cleaned_subs
            cleaned_subs.append(pysrt.SubRipItem(start=prev_sub.start, end=merged_end, text=merged_text))'''
        # Save the cleaned subtitles to a new file
        #base_name = os.path.splitext(file_path)[0]
        #new_file_path = base_name + '.cleaned.srt'
        #subs.save(new_file_path, encoding='utf-8')
        parent_dir = cd
        base_name = os.path.basename(file_path)
        new_file_path = os.path.join(parent_dir, base_name)
        cleaned_sub_file.save(new_file_path, encoding='utf-8')
        # Load the SRT file
        dup = True
        if dup:
            subs = pysrt.open(new_file_path)
            unique_lines = set()
            unique_subs = []
            # Iterate through each subtitle
            i = 0
            lastI = 0
            lastS = ''
            for sub in subs:
                # Strip leading/trailing whitespace and convert to lowercase for comparison
                cleaned_line = sub.text.strip()#.lower()

                # compare last and - i <= 3
                isl = cleaned_line in unique_lines
                dif = i - lastI
                print(i,lastI,isl,len(unique_lines))
                if len(str(cleaned_line)) > 1:
                    if cleaned_line in unique_lines:
                        if dif > 3 or lastS != cleaned_line:
                            unique_subs.append(sub)
                        elif dif == 1:
                            try:
                                d = subs[i-1].end
                                j = i
                                df = 0
                                print(d,sub.end,i)
                                while df <= 1:
                                    d = subs[j].start
                                    df = (d-sub.end).seconds
                                    print(d,d-sub.end,j,df,d.seconds)
                                    j += 1
                                if df > 1:
                                    subs[i-1].end = d
                                else:
                                    raise Exception()
                            except Exception as de:
                                exc_type, exc_obj, exc_tb = sys.exc_info()
                                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                                print(de,exc_type, fname, exc_tb.tb_lineno)
                                subs[i-1].end += pysrt.SubRipTime(seconds=3)
                    elif cleaned_line not in unique_lines:
                        unique_lines.add(cleaned_line)
                        unique_subs.append(sub)
                    if cleaned_line in unique_lines:
                        lastI = i
                        lastS = cleaned_line
                i += 1
            # Create a new SubRipFile object with the unique subtitles
            cleaned_sub_file = pysrt.SubRipFile(unique_subs)

            # Save the cleaned subtitles to the same file path
            cleaned_sub_file.save(new_file_path, encoding='utf-8')
        log_entry = f'Processed: {file_path}\n'
        log_entry += f'lines: {unique_lines} {cleaned_subs}\n'
        log_entry += f'Cleaned file: {new_file_path}\n\n'
        log_file.write(log_entry)
        print(log_entry.strip())
        print(f'Subtitles cleaned successfully. {unique_lines} {cleaned_subs} Cleaned file: {new_file_path}')
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
    if not all(s in current_directory for s in strings):
        source_files = [
            "C:\\Users\\halff\\Documents\\.scriptbat\\subs.py",
            "C:\\Users\\halff\\Documents\\.scriptbat\\quicksrt=-ass.bat",
            "C:\\Users\\halff\\Documents\\.scriptbat\\subsdelay.bat",
            "C:\\Users\\halff\\Documents\\.scriptbat\\quickdefault.bat",
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
    shutil.move(file_path, dest)
    log_file_path = os.path.join(dirr, 'srt_log.txt')
    try:
        # Create a backup by moving the original file to the backup directory

        # Check if 'seconds' argument is provided
        # Clean the subtitle file and save the cleaned version with the same name as the original
        clean_srt_file(backup_path, log_file_path, dirr)
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