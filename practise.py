from src.s3_syncer import S3Sync
from datetime import datetime

import os

import re

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
    
# conversation = ["speaker1: hi", "speaker2: hello", "speaker1: bye", "speaker2: ok bye"]
conversation =  ["<strong>Speaker 1:</strong> Now let's talk about email. What kind of emails do you receive about your work?",
"<strong>Speaker 2:</strong> I receive a lot of emails from my higher ups. So my manager, people from other departments as well, usually following up for things, um, or scheduling meetings. Um, just a lot of work that needs to be done and reminders to please do this work."
,"<strong>Speaker 1:</strong> So do you normally reply to emails as soon as you receive them?"]
directory_path = save_transcription(conversation)

# TRAINING_BUCKET_NAME = "focus-transcribe"
# timestamp = datetime.now()
# timestamp = timestamp.strftime("%m_%d_%y_%H_%M_%S")

# s3_sync = S3Sync()


# aws_bucket_url = f"s3://{TRAINING_BUCKET_NAME}/artifact/{timestamp}"
# s3_sync.sync_folder_to_s3(folder = directory_path,aws_bucket_url=aws_bucket_url)


# aws s3 rm s3://your-bucket-name --recursive