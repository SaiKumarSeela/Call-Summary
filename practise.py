from pydub import AudioSegment
import os

audio_path = "C:\\Users\\Sheela Sai kumar\\Documents\\UPSkilling\\ML\\Call-Summary\\YoutubeAudios\\audio1.mp3"


audio = AudioSegment.from_file(audio_path, format="mp3")
audio.export("output_file.wav", format="wav")