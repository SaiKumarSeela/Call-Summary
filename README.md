# Call-Summary

Call-Summary is a Python application designed to summarize audio transcripts using advanced AI models. This project utilizes the GROQ and AssemblyAI APIs to transcribe and summarize audio content effectively.

## Features

- **Audio Summarization**: Automatically generates concise summaries of audio transcripts.
- **Audio Trimming**: Use the online tool [Audio Trimmer](https://audiotrimmer.com/#) to trim audio files before summarization.

## Prerequisites

To run this application, you need to obtain two API keys:

1. **GROQ_API_KEY**: Sign up and create an API key at [GROQ Console](https://console.groq.com/keys).
2. **ASSEMBLYAI_API_KEY**: Create an account and get your API key from [AssemblyAI Dashboard](https://www.assemblyai.com/dashboard/signup).

## Installation

Follow these steps to set up the project:

1. Clone the repository:
   ```bash
   git clone https://github.com/SaiKumarSeela/Call-Summary.git
   cd Call-Summary
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set your API keys in a `.env` file or directly in your script.

## Running the Application

To run the application, execute the following command in your terminal:

```bash
python main.py
```

## Usage

1. Provide the YouTube URL or local audio file for transcription.
2. The application will process the audio and generate a summary.
3. Optionally, you can trim your audio using [Audio Trimmer](https://audiotrimmer.com/#) before summarization.


