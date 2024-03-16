### GENERATE EMBEDDINGS DICTIONARY FROM ALL VIDEOS ON YOUTUBE CHANNEL ###

from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
import os
import json
from tqdm import tqdm

# Group transcript entries (~10 words each) into groups of 20 with 20% overlap
def group_transcript_entries(transcript):
    grouped_transcripts = []
    group_size = 20
    overlap = 4

    for i in range(0, len(transcript), group_size - overlap):
        group = transcript[i:i + group_size]
        group_text = " ".join([entry['text'] for entry in group])
        grouped_transcripts.append((group[0]['start'], group_text))

    return grouped_transcripts

# Format grouped transcripts into a list
def format_transcript_to_list(grouped_transcripts, video_id, summary):
    formatted_transcript = []
    
    for start_time, group_text in grouped_transcripts:
        formatted_transcript.append({"excerpt link" : f"https://www.youtube.com/watch?v={video_id}&t={int(start_time)}s", 
                                     "transcript excerpt" : group_text,
                                     "video summary" : summary})

    return formatted_transcript

# Extract transcipt
def get_video_transcript(video_id):
    # Load api key from env
    load_dotenv()
    api_key = os.getenv("YOUTUBE_API_KEY")
    
    # Build the YouTube API client
    youtube = build('youtube', 'v3', developerKey=api_key)

    # Try to fetch the caption track list
    try:
        response = youtube.captions().list(
            part='snippet',
            videoId=video_id
        ).execute()
    except Exception as e:
        print(f"Error fetching caption tracks: {e}")
        return None

    # Check if captions are available
    if not response['items']:
        print("No captions available for this video.")
        return None

    # Extracting the transcript using the youtube_transcript_api
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        # Grouping the transcript entries
        grouped_transcripts = group_transcript_entries(transcript)
        # Get video description to summarize
        video_description = get_video_description(video_id)
        # Get the summary
        summary = get_summary(video_description)
        # Formatting the grouped transcript to dictionary
        formatted_transcript = format_transcript_to_list(grouped_transcripts, video_id, summary)
        return formatted_transcript

    except Exception as e:
        print(f"Error fetching transcript: {e}")
        return None

# generate the transcripts list
transcripts_list = []

for id in tqdm(video_ids):
    transcript_list = get_video_transcript(id)
    if transcript_list:
        transcripts_list += transcript_list

# Saving the list to a new JSON file
dirname = os.getcwd()
output_file_path = os.path.join(dirname, 'data/wb_youtube_videos_complete.json')
with open(output_file_path, 'w') as output_file:
    json.dump(transcripts_list, output_file, indent=4)