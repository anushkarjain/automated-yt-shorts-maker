import os
import subprocess
import logging
from yt_dlp import YoutubeDL
import json

logging.basicConfig(level=logging.INFO)

def download_videos(videos, output_folder="downloads"):
    """Download videos using yt_dlp."""
    os.makedirs(output_folder, exist_ok=True)
    with YoutubeDL({'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s')}) as ydl:
        ydl.download(videos)

def split_video(input_file, edit_folder="edits", segment_duration=45):
    """Split video into segments if it's a .webm file."""
    if input_file.endswith('.webm'):
        output_pattern = os.path.join(edit_folder, 'edit_%03d.mp4')
        command = [
            'ffmpeg',
            '-i', input_file,
            '-c', 'copy',
            '-f', 'segment',
            '-segment_time', str(segment_duration),
            output_pattern
        ]
        subprocess.run(command)
        logging.info(f"{input_file} has been split into segments.")

def crop_to_aspect_ratio(folder_path, new_aspect_ratio="9:16", op_folder_path="final"):
    """Crops all MP4 videos in a folder to the specified aspect ratio."""
    os.makedirs(op_folder_path, exist_ok=True)
    video_files = [file for file in os.listdir(folder_path) if file.endswith('.mp4')]
    
    for file in video_files:
        input_file_path = os.path.join(folder_path, file)
        output_file_path = os.path.join(op_folder_path, f"cropped_{file}")

        try:
            input_width, input_height = get_video_dimensions(input_file_path)
            output_width, output_height = calculate_dimensions_for_aspect_ratio(new_aspect_ratio, input_width, input_height)
            crop_width = (input_width - output_width) // 2
            crop_height = 0

            command = f"ffmpeg -i {input_file_path} -vf 'scale={output_width}:{output_height},crop={output_width}:{output_height}:{crop_width}:{crop_height}' -c:v libx264 -crf 18 -preset veryfast {output_file_path}"
            subprocess.run(command, shell=True)
            logging.info(f"{file} has been cropped to {new_aspect_ratio}.")
        except Exception as e:
            logging.error(f"Error processing {file}: {e}")

def get_video_dimensions(file_path):
    """Retrieve video dimensions using ffprobe."""
    with subprocess.Popen(["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", file_path], stdout=subprocess.PIPE) as proc:
        video_info = json.loads(proc.stdout.read())
        return int(video_info["streams"][0]["coded_width"]), int(video_info["streams"][0]["coded_height"])

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

if __name__ == "__main__":
    videos = ['(video link)']
    download_videos(videos)

    for file in os.listdir("downloads"):
        if file.endswith(".webm"):
            split_video(os.path.join("downloads", file))

    crop_to_aspect_ratio("edits")
