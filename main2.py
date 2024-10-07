import streamlit as st
import numpy as np
import os
from dotenv import load_dotenv
from src.summarization import summarise_transcript
from deepgram import DeepgramClient, PrerecordedOptions
from src.utils import count_words
import io
from datetime import datetime
from src.s3_syncer import S3Sync
import re
import pandas as pd
import base64

# Load environment variables
load_dotenv()

# Initialize the Deepgram client
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
GROQ_API = os.getenv("GROQ_API_KEY")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
deepgram = DeepgramClient(DEEPGRAM_API_KEY)
TRAINING_BUCKET_NAME = "focus-transcribe"
timestamp = datetime.now().strftime("%m_%d_%y_%H_%M_%S")
s3_sync = S3Sync(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION)

# Store speaker-specific recordings and transcriptions
if 'speakers_data' not in st.session_state:
    st.session_state.speakers_data = {}
if 'selected_speaker' not in st.session_state:
    st.session_state.selected_speaker = None
if 'conversation' not in st.session_state:
    st.session_state.conversation = []

# Function to transcribe audio using Deepgram API
def transcribe_audio(base64_audio):
    audio_data = io.BytesIO(base64.b64decode(base64_audio))
    source = {"buffer": audio_data.read(), "mimetype": "audio/wav"}
    options = PrerecordedOptions(model="nova", language="en-US")
    response = deepgram.listen.prerecorded.v("1").transcribe_file(source, options)
    return response.results.channels[0].alternatives[0].transcript

# Save transcription to a file
def save_transcription(conversation):
    directory = 'transcriptions'
    if not os.path.exists(directory):
        os.makedirs(directory)

    full_transcription_file = os.path.join(directory, 'transcription_with_speakers.txt')
    no_speakers_file = os.path.join(directory, 'transcription_with_no_speakers.txt')

    with open(full_transcription_file, 'w') as file_full, open(no_speakers_file, 'w') as file_no_speakers:
        for entry in conversation:
            entry_no_tags = re.sub(r'<.*?>', '', entry)
            file_full.write(entry_no_tags + '\n')
            entry_without_speaker = entry_no_tags.split(': ', 1)[-1]
            file_no_speakers.write(entry_without_speaker + ' ')
    
    return directory

# Extract texts by speaker
def extract_speaker_texts(conversation):
    speaker_texts = {}
    for entry in conversation:
        speaker, text = entry.split(': ', 1)
        if speaker not in speaker_texts:
            speaker_texts[speaker] = []
        speaker_texts[speaker].append(text)
    return {speaker: ' '.join(texts) for speaker, texts in speaker_texts.items()}

# UI for selecting speakers
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

# JavaScript to capture live audio from the browser
st.markdown("""
    <script>
        let mediaRecorder;
        let audioChunks = [];

        function startRecording() {
            navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
                mediaRecorder = new MediaRecorder(stream);
                mediaRecorder.start();
                mediaRecorder.ondataavailable = event => {
                    audioChunks.push(event.data);
                };
            });
        }

        function stopRecording() {
            mediaRecorder.stop();
            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunks, { 'type': 'audio/wav' });
                audioChunks = [];
                const reader = new FileReader();
                reader.readAsDataURL(audioBlob);
                reader.onloadend = () => {
                    const base64AudioMessage = reader.result.split(',')[1];

                    // Send audio data to the backend
                    fetch('/transcribe', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ audio: base64AudioMessage })
                    }).then(response => response.json())
                    .then(data => {
                        console.log(data.transcription);
                        document.getElementById('transcription').innerText = data.transcription;
                    });
                };
            };
        }
    </script>

    <button onclick="startRecording()">Start Recording</button>
    <button onclick="stopRecording()">Stop Recording</button>
    <p id="transcription">Transcription will appear here...</p>
""", unsafe_allow_html=True)

# Handle POST request for transcription
if st.experimental_get_query_params().get('path_info') == '/transcribe':
    data = st.experimental_get_query_params().get('data')
    audio = data.get('audio')
    
    if audio:
        transcript = transcribe_audio(audio)
        st.session_state.conversation.append(f"{st.session_state.selected_speaker}: {transcript}")
        st.write({'transcription': transcript})

# Display transcriptions
if st.button("Show All Transcriptions"):
    for entry in st.session_state.conversation:
        st.write(entry)

# Save transcriptions to S3 bucket
if st.button("Save Transcriptions"):
    if st.session_state.conversation:
        save_dir = save_transcription(st.session_state.conversation)
        s3_sync.sync_folder_to_s3(folder=save_dir, aws_bucket_name=TRAINING_BUCKET_NAME)
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