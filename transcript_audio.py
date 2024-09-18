import speech_recognition as sr
import os

def transcribe_audio(audio_file):
    recognizer = sr.Recognizer()
    
    try:
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)  # Read the entire audio file
            transcription = recognizer.recognize_google(audio_data)  # Using Google Web Speech API
            
            print("Transcription:")
            print(transcription)
            return transcription  # Return the transcription text

    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")

if __name__ == "__main__":
    audio_file = "YoutubeAudios/audio1.mp3"  # Replace with your audio file path
    if os.path.exists(audio_file):
        transcribe_audio(audio_file)
    else:
        print(f"Audio file '{audio_file}' does not exist.")