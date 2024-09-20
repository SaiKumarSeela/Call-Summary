from os import path
from pydub import AudioSegment
from pytube import YouTube
from moviepy.editor import *
import os
import assemblyai as aai
import json


def convertmp3_to_wav(input_file_path, output_file_path):
    # Convert MP3 to WAV
    sound = AudioSegment.from_mp3(input_file_path)
    sound.export(output_file_path, format="wav")

    return output_file_path


def extract_audio_from_youtube(youtube_url):
    try:
        # Create a YouTube object with the provided URL
        video = YouTube(youtube_url)

        # Filter for audio streams and select the first available one
        audio_stream = video.streams.filter(only_audio=True).first()

        # Download the audio stream
        audio_stream.download()

        video_path =audio_stream.default_filename
        audio_path = video_path.replace(".mp4",".mp3")

        clip = AudioFileClip(video_path) # type: ignore
        clip.write_audiofile(audio_path)
        
        os.remove(video_path)
        return audio_path

    except Exception as e:
        print(f"An error occurred: {e}")

def get_transcript_using_assemblyai(assembly_api_key, mp3file_path):
    aai.settings.api_key = assembly_api_key 

    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(mp3file_path)

    if transcript.status == aai.TranscriptStatus.error:
        return transcript.error
    else:
        return transcript.text
    
