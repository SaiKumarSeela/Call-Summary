from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv
import assemblyai as aai

load_dotenv()

assembly_api_key = os.getenv("ASSEMBLYAI_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")

def get_transcript(assembly_api_key, mp3file_path):
    aai.settings.api_key = assembly_api_key 

    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(mp3file_path)

    if transcript.status == aai.TranscriptStatus.error:
        return transcript.error
    else:
        return transcript.text

llm = ChatGroq(
    groq_api_key=groq_api_key,
    model_name="Llama3-8b-8192"
)

def summarise_transcript(mp3file_path):
    # Get the transcript from the audio file
    transcript = get_transcript(assembly_api_key=assembly_api_key, mp3file_path=mp3file_path)

    # Prepare the prompt for summarization
    summarise_prompt = f""" Summarise the following transcript delimited by 3 backticks: {transcript} """

    # Create the chat message structure for Groq API
    messages = [
        {
            'role': 'system',
            'content': 'You are a helpful assistant who summarises the provided text concisely in no more than 1000 words.'
        },
        {
            'role': 'user',
            'content': summarise_prompt,
        },
    ]

    # Get the response from the Llama model
    response = llm.invoke(messages)

    print(type(response))

    # Extract and print only the content from the response
    summary_content = response.content
    print("Summary:", summary_content)


# Example usage
if __name__ == "__main__":
    mp3file_path = "Samples/chunk1.mp3" 
    summarise_transcript(mp3file_path)