import streamlit as st
import json
import os
from src.logger import logging
from src.dairization import WhisperTranscriber
import time
from dotenv import load_dotenv

load_dotenv()

huggingface_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")

def display_conversation(filename='data.json', uniq_speakers=None):
    logging.info("Display the conversation from the JSON file.")
    
    with open(filename, 'r') as file:
        data = json.load(file)

    # Create dynamic speaker mapping based on unique speakers
    if uniq_speakers is None:
        uniq_speakers = list(set(segment['speaker'] for segment in data['segments']))

    speaker_map = {speaker: f"Speaker {i + 1}" for i, speaker in enumerate(uniq_speakers)}

    conversation = []
    current_speaker = None
    current_text = ""

    for segment in data['segments']:
        speaker = segment['speaker']
        text = segment['text'].strip()

        if speaker == current_speaker:
            # If the same speaker continues, append to current text
            current_text += f" {text}"
        else:
            # If a new speaker starts, save the previous text and reset
            if current_speaker is not None:
                conversation.append(f"**{speaker_map[current_speaker]}:** {current_text.strip()}")  # Add previous speaker's text
            
            # Update to the new speaker
            current_speaker = speaker
            current_text = text

    # Don't forget to add the last speaker's text after the loop
    if current_speaker is not None:
        conversation.append(f"**{speaker_map[current_speaker]}:** {current_text.strip()}")

    # Display the complete conversation
    for line in conversation:
        st.markdown(line)

def main(huggingface_token):
    st.title("Audio Transcription and Speaker Diarization")

    audio_file = st.file_uploader("Upload an audio file (.wav or .mp3)", type=['wav', 'mp3'])

    if audio_file is not None:
        # Save uploaded audio file
        with open("uploaded_audio.wav", "wb") as f:
            f.write(audio_file.getbuffer())

        transcriber = WhisperTranscriber("uploaded_audio.wav", huggingface_token)
        
        
        
        # Initialize process tracking
        steps_completed = {
            "model_loaded": False,
            "transcribed": False,
            "aligned": False,
            "diarized": False,
            "saved": False
        }
        # Load model if not already loaded
        if 'model' not in st.session_state:
            with st.spinner("Loading model..."):
                transcriber.load_model()
                steps_completed["model_loaded"] = True
                st.session_state.model_loaded = True  # Track model loading status
                st.markdown("✅ Model Loaded completed!")  # Immediate feedback

        # Cancel button to stop processing
        cancel_button_clicked = st.button("Cancel")

        if cancel_button_clicked:
            transcriber.cancel_process = True  # Set cancellation flag
            st.warning("Processing has been canceled.")
        
        if not transcriber.cancel_process:
            transcriber.start_process()  # Record start time

            # Process audio file steps with loaders
            with st.spinner("Transcribing audio..."):
                transcriber.transcribe_audio()
                steps_completed["transcribed"] = True
                st.markdown("✅ Transcribing completed!")  # Immediate feedback

            if not transcriber.cancel_process:
                with st.spinner("Aligning transcription..."):
                    transcriber.align_transcription()
                    steps_completed["aligned"] = True
                    st.markdown("✅ Alignment completed!")  # Immediate feedback

            if not transcriber.cancel_process:
                with st.spinner("Diarizing audio..."):
                    final_result, uniq_speakers = transcriber.diarize_audio()
                    steps_completed["diarized"] = True
                    st.markdown("✅ Diarization completed!")  # Immediate feedback

            if not transcriber.cancel_process:
                # Save results to JSON
                transcriber.save_to_json(final_result)
                steps_completed["saved"] = True
                st.markdown("✅ Saving completed!")  # Immediate feedback

            if not transcriber.cancel_process:
                elapsed_time = transcriber.end_process()  # Record end time and calculate elapsed time
                st.success(f"Audio processing complete in {elapsed_time:.2f} seconds!")

                # Display completed steps with tick marks
                # for step, completed in steps_completed.items():
                #     if completed:
                #         st.markdown(f"✅ **{step.replace('_', ' ').title()}** completed!")
                #     else:
                #         st.markdown(f"❌ **{step.replace('_', ' ').title()}** not completed!")

                st.subheader("Conversation")
                display_conversation(filename='data.json',uniq_speakers= uniq_speakers)

if __name__ == "__main__":
    main(huggingface_token)