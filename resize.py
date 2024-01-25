import os
from moviepy.editor import VideoFileClip

def resize_videos(input_folder, output_folder, target_width, target_height):
    # Iterate through all files in the input folder
    for file in os.listdir(input_folder):
        if file.endswith('.mp4'):  # Check if the file is a video file
            # Construct paths for input and output videos
            input_video_path = os.path.join(input_folder, file)
            output_video_path = os.path.join(output_folder, file)
            
            # Load the video clip
            clip = VideoFileClip(input_video_path)
            
            # Resize the video to the target dimensions
            resized_clip = clip.resize((target_width, target_height))
            
            # Write the resized video to a new file
            resized_clip.write_videofile(output_video_path)
            
            # Close the video clip
            clip.close()

# Example usage
input_folder = "final"  # Folder containing input videos
output_folder = "resized_final"  # Folder to save resized videos
target_width = 1080  # Target width for YouTube Shorts
target_height = 1920  # Target height for YouTube Shorts

# Create the output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Resize all videos in the input folder
resize_videos(input_folder, output_folder, target_width, target_height)
