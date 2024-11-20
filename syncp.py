import os
import subprocess
import re

# Define the directories
video_dir = r'e:\pokemon 2019'
srt_dir = r'c:\Users\halff\Documents\Subs\pokemon 2019'

# Function to extract episode number from filename
def extract_episode_number(filename):
    match = re.search(r'(\d+)', filename)
    return match.group(1) if match else None

# List all MKV files in the video directory
mkv_files = [f for f in os.listdir(video_dir) if f.endswith('.mkv')]

# Process each MKV file
for mkv_file in mkv_files:
    episode_number = extract_episode_number(mkv_file)
    
    if episode_number:
        # Construct the corresponding SRT filename
        srt_file_pattern = f'pocket_monsters_2019*{episode_number}*.srt'
        srt_files = [f for f in os.listdir(srt_dir) if re.match(srt_file_pattern, f, re.IGNORECASE)]
        
        for srt_file in srt_files:
            # Define input and output file paths
            video_path = os.path.join(video_dir, mkv_file)
            srt_path = os.path.join(srt_dir, srt_file)
            output_srt_path = os.path.join(srt_dir, f'corrected_{srt_file}')
            
            # Construct the alass command
            command = [
                'alass',
                video_path,
                srt_path,
                output_srt_path,
                '--disable-fps-guessing',
                '--split-penalty',
                '10'
            ]
            
            # Execute the command
            print(f'Running command: {" ".join(command)}')
            subprocess.run(command)

print("Subtitle syncing completed.")