# use "python3 merge.py" to run this file

import os
import subprocess
from yt_dlp import YoutubeDL

# Download videos using yt_dlp
def download_videos(videos, output_folder="downloads"):
    os.makedirs(output_folder, exist_ok=True)
    with YoutubeDL({'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s')}) as ydl:
        ydl.download(videos)

# Split video into segments if it's a .webm file
def split_video(input_file, edit_folder="edits", segment_duration=45):
    if input_file.endswith('.webm'):  # Conditionally split only .webm files
        output_pattern = os.path.join(edit_folder, 'edit_%03d.mp4')  # Output as MP4
        command = [
            'ffmpeg',
            '-i', input_file,
            '-c', 'copy',
            '-f', 'segment',
            '-segment_time', str(segment_duration),
            output_pattern
        ]
        subprocess.run(command)

# Crop videos to a specified aspect ratio if it's an .mp4 file
def crop_to_aspect_ratio(folder_path, new_aspect_ratio="9:16", op_folder_path="final"):
    """Crops all MP4 videos in a folder to the specified aspect ratio."""

    import json  # Import only when needed for this function

    video_files = [file for file in os.listdir(folder_path) if file.endswith('.mp4')]

    for file in video_files:
        input_file_path = os.path.join(folder_path, file)
        output_file_path = os.path.join(op_folder_path, f"cropped_{file}")

        with subprocess.Popen(["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", input_file_path], stdout=subprocess.PIPE) as proc:
            video_info = json.loads(proc.stdout.read())
            input_width, input_height = int(video_info["streams"][0]["coded_width"]), int(video_info["streams"][0]["coded_height"])

        output_width, output_height = calculate_dimensions_for_aspect_ratio(new_aspect_ratio, input_width, input_height)
        crop_width = (input_width - output_width) // 2
        crop_height = 0

        command = f"ffmpeg -i {input_file_path} -vf 'scale={output_width}:{output_height},crop={output_width}:{output_height}:{crop_width}:{crop_height}' -c:v libx264 -crf 18 -preset veryfast {output_file_path}"
        subprocess.run(command, shell=True)

        print(f"{file} has been cropped to {new_aspect_ratio}.")

def calculate_dimensions_for_aspect_ratio(aspect_ratio, input_width, input_height):
    """Calculates output dimensions for a given aspect ratio, preserving aspect ratio."""

    aspect_ratio_width, aspect_ratio_height = map(int, aspect_ratio.split(":"))
    desired_aspect_ratio = aspect_ratio_width / aspect_ratio_height
    current_aspect_ratio = input_width / input_height

    if desired_aspect_ratio > current_aspect_ratio:
        output_width = input_width
        output_height = int(input_width / desired_aspect_ratio)
    else:
        output_height = input_height
        output_width = int(input_height * desired_aspect_ratio)

    return output_width, output_height

# Example usage
videos = ['https://www.youtube.com/watch?v=2NqO7ugDy6w']
download_videos(videos)

# Split all .webm files in the "downloads" folder
for file in os.listdir("downloads"):
    if file.endswith(".webm"):
        split_video(os.path.join("downloads", file))

# Crop videos in the "edits" folder (if they're .mp4)
crop_to_aspect_ratio("edits")  # Output to the "final" folder

