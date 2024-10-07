import streamlit as st
import numpy as np
import sounddevice as sd
from scipy.io import wavfile
import os
from dotenv import load_dotenv
from src.summarization import summarise_transcript
from deepgram import DeepgramClient, PrerecordedOptions
from src.utils import count_words
import io
from datetime import datetime
from src.s3_syncer import S3Sync
import time
import re
import pandas as pd

# Load environment variables
load_dotenv()

# Initialize the Deepgram client
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
GROQ_API = os.getenv("GROQ_API_KEY")
deepgram = DeepgramClient(DEEPGRAM_API_KEY)
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
TRAINING_BUCKET_NAME = "focus-transcribe"
timestamp = datetime.now()
timestamp = timestamp.strftime("%m_%d_%y_%H_%M_%S")
s3_sync = S3Sync()

# Audio recording parameters
SAMPLE_RATE = 16000  # 16 kHz sample rate for better compatibility
CHANNELS = 1  # Mono channel

# Store speaker-specific recordings and transcriptions
if 'speakers_data' not in st.session_state:
    st.session_state.speakers_data = {}
if 'selected_speaker' not in st.session_state:
    st.session_state.selected_speaker = None
if 'conversation' not in st.session_state:
    st.session_state.conversation = []

def transcribe_audio(audio_data):
    byte_io = io.BytesIO()
    wavfile.write(byte_io, SAMPLE_RATE, audio_data)
    audio_bytes = byte_io.getvalue()

    source = {"buffer": audio_bytes, "mimetype": "audio/wav"}
    options = PrerecordedOptions(model="nova", language="en-US")

    response = deepgram.listen.prerecorded.v("1").transcribe_file(source, options)
    return response.results.channels[0].alternatives[0].transcript

def save_transcription(conversation):
    directory = 'transcriptions'
    if not os.path.exists(directory):
        os.makedirs(directory)

    full_transcription_file = os.path.join(directory, 'transcription_with_speakers.txt')
    no_speakers_file = os.path.join(directory, 'transcription_with_no_speakers.txt')

    # Empty the existing files if present
    open(full_transcription_file, 'w').close()
    open(no_speakers_file, 'w').close()

    with open(full_transcription_file, 'a') as file_full:
        with open(no_speakers_file, 'a') as file_no_speakers:
            for entry in conversation:
                # Remove HTML tags for full transcription
                entry_no_tags = re.sub(r'<.*?>', '', entry)
                file_full.write(entry_no_tags + '\n')
                
                # Remove speaker name for no speakers transcription
                entry_without_speaker = entry_no_tags.split(': ', 1)[-1]
                file_no_speakers.write(entry_without_speaker + ' ')
    
    return directory



def extract_speaker_texts(conversation):
    speaker_texts = {}
    for entry in conversation:
        speaker, text = entry.split(': ', 1)
        if speaker not in speaker_texts:
            speaker_texts[speaker] = []
        speaker_texts[speaker].append(text)
    return {speaker: ' '.join(texts) for speaker, texts in speaker_texts.items()}

st.title("Deepgram Transcription for Multiple Speakers")

if 'num_speakers' not in st.session_state:
    num_speakers = st.number_input("Enter the number of speakers:", min_value=1, max_value=10, value=2)
    if st.button("Create Speaker Buttons"):
        for i in range(num_speakers):
            speaker_name = f"Speaker{i+1}"
            st.session_state.speakers_data[speaker_name] = {"audio_data": None, "transcript": None, "duration": None}
else:
    num_speakers = len(st.session_state.speakers_data)

# Create buttons for each speaker
for speaker in st.session_state.speakers_data.keys():
    if st.button(f"{speaker}", key=speaker):
        st.session_state.selected_speaker = speaker

if st.session_state.selected_speaker:
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Start Recording"):
            st.session_state.start_time = time.time()  # Store the start time
            st.session_state.recording = sd.rec(int(60 * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=CHANNELS, dtype='int16')
            st.success(f"{st.session_state.selected_speaker} started recording.")
    
    with col2:
        if st.button("Stop Recording"):
            sd.stop()
            st.session_state.speakers_data[st.session_state.selected_speaker]['duration'] = time.time() - st.session_state.start_time  # Calculate duration
            st.session_state.speakers_data[st.session_state.selected_speaker]['audio_data'] = st.session_state.recording[:int(SAMPLE_RATE * st.session_state.speakers_data[st.session_state.selected_speaker]['duration'])].flatten()
            st.success(f"{st.session_state.selected_speaker} stopped recording.")
    
    if st.button("Transcribe"):
        audio_data = st.session_state.speakers_data[st.session_state.selected_speaker]['audio_data']
        if audio_data is not None:
            with st.spinner("Transcribing..."):
                transcript = transcribe_audio(audio_data)
                st.session_state.speakers_data[st.session_state.selected_speaker]['transcript'] = transcript
                st.session_state.conversation.append(f"{st.session_state.selected_speaker}: {transcript}")
                st.subheader(f"Transcription for {st.session_state.selected_speaker}:")
                st.write(f"{st.session_state.selected_speaker}: {transcript}")
        else:
            st.warning("Please record audio first.")

# Display all transcriptions
if st.button("Show All Transcriptions"):
    for entry in st.session_state.conversation:
        st.write(entry)

# Save transcriptions
if st.button("Save Transcriptions"):
    if st.session_state.conversation:
    
        save_dir = save_transcription(st.session_state.conversation)
        aws_bucket_url = f"s3://{TRAINING_BUCKET_NAME}/transcription/{timestamp}"
        s3_sync.sync_folder_to_s3(folder = save_dir,aws_bucket_url=aws_bucket_url)
        print("Succesfully transcriptions are saved to s3 bucket")
        st.success(f"Transcriptions saved in {save_dir}")
    else:
        st.warning("No transcriptions to save.")

# Generate summary
if st.button("Generate Summary"):
    if st.session_state.conversation:
        speaker_texts = extract_speaker_texts(st.session_state.conversation)
        individual_summary = {}
        for speaker, speeches in speaker_texts.items():
            individual_summary[speaker] = summarise_transcript(groq_api_key=GROQ_API, transcript=speeches)
        
        summary_content = summarise_transcript(groq_api_key=GROQ_API,  transcript=' '.join(st.session_state.conversation))
        
        summary_data = {
            "Speaker": list(individual_summary.keys()) + ["Total Summary"],
            "Summary": list(individual_summary.values()) + [summary_content]
        }
        
        st.subheader("Summaries")
        st.table(pd.DataFrame(summary_data))
    else:
        st.warning("No transcriptions available for summarization.")
if st.button("Get Stats"):
    if st.session_state.conversation:

        total_words, words_by_speaker = count_words(st.session_state.conversation)
        stat_data = {
        'Total Words': [total_words],
        }
        # Add words by each speaker dynamically to the DataFrame
        for speaker, word_count in words_by_speaker.items():
            stat_data[f'Words by {speaker}'] = [word_count]

        stats_df = pd.DataFrame(stat_data)
        stats_df.to_csv("output.csv", index=False)
        # st.subheader("Statistics")
        st.table(stats_df)
    else:
        st.warning("No stats should be displayed.")