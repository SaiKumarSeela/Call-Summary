from pytube import YouTube
from moviepy.editor import *
import os

def extract_audio(youtube_url):
    try:
        # Create a YouTube object with the provided URL
        video = YouTube(youtube_url)

        # Filter for audio streams and select the first available one
        audio_stream = video.streams.filter(only_audio=True).first()

        # Download the audio stream
        audio_stream.download()

        video_path =audio_stream.default_filename
        audio_path = video_path.replace(".mp4",".mp3")

        clip = AudioFileClip(video_path)
        clip.write_audiofile(audio_path)
        
        os.remove(video_path)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Replace with your desired YouTube video URL
    youtube_url = input("Enter the YouTube video URL: ")
    # youtube_url = "https://youtu.be/rkR4sFODnIM"
    # Specify the destination folder (leave blank for current directory)

    extract_audio(youtube_url)