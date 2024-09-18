import os
from pydub import AudioSegment
import speech_recognition as sr

def extract_transcript(mp3_file_path):
    # Convert MP3 to WAV format
    wav_file_path = "temp.wav"
    audio = AudioSegment.from_mp3(mp3_file_path)
    audio.export(wav_file_path, format="wav")
    
    # Initialize recognizer
    recognizer = sr.Recognizer()
    
    # Load the WAV file for transcription
    with sr.AudioFile(wav_file_path) as source:
        audio_data = recognizer.record(source)  # Read the entire WAV file
    
    try:
        # Transcribe audio to text using Google Web Speech API
        transcript = recognizer.recognize_google(audio_data)
        print("Transcript: ", transcript)
        return transcript
    
    except sr.UnknownValueError:
        print("Google Web Speech API could not understand audio")
        return None
    
    except sr.RequestError as e:
        print(f"Could not request results from Google Web Speech API; {e}")
        return None
    
    finally:
        # Clean up temporary WAV file
        if os.path.exists(wav_file_path):
            os.remove(wav_file_path)

# Example usage
mp3_file = "YoutubeAudios\\audio1.mp3"
transcript_text = extract_transcript(mp3_file)


