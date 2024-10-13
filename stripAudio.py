import os
from moviepy.editor import VideoFileClip

def strip_audio(input_folder, output_folder):
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Iterate through all files in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith('.MP4'):  # Add more formats if needed
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)

            # Load the video file
            print(f"Processing: {filename}")
            video = VideoFileClip(input_path)

            # Remove audio
            video_without_audio = video.volumex(0)  # Set volume to 0
            video_without_audio.write_videofile(output_path, codec='libx264')

            # Close the video objects
            video.close()
            video_without_audio.close()

            # Delete the original video
            os.remove(input_path)
            print(f"Deleted original video: {filename}")

if __name__ == "__main__":
    fileFormats = [".mp4", ".MP4"]
    input_folder = "/Users/alexjshepler/Hackathons/DubHacks2024/videos/Original"
    output_folder = "/Users/alexjshepler/Hackathons/DubHacks2024/videos/NoAudio"
    strip_audio(input_folder, output_folder)