### GENERATE VIDEO ID LIST FROM YOUTUBE CHANNEL ###

from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI
from dotenv import load_dotenv
import os
from tqdm import tqdm
from settings import (
    OPENAI_API_KEY,
    YOUTUBE_API_KEY,
)

# Function to get all video ids from a channel
def get_all_video_ids(channel_id):
    # Load api key from env
    load_dotenv()
    api_key = YOUTUBE_API_KEY

    # Initialize list
    video_ids = []

    # Get the channel's content details
    youtube = build('youtube', 'v3', developerKey=api_key)
    channel_response = youtube.channels().list(
        id=channel_id,
        part='contentDetails'
    ).execute()

    # Get the playlist ID for the channel's videos
    playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    # Get videos from the playlist
    next_page_token = None
    while True:
        playlist_response = youtube.playlistItems().list(
            playlistId=playlist_id,
            part='contentDetails',
            maxResults=50,
            pageToken=next_page_token
        ).execute()

        video_ids += [item['contentDetails']['videoId'] for item in playlist_response['items']]
        
        # Add tqdm progress bar
        for i in tqdm(range(len(playlist_response['items']))):
            pass

        # Check if there is a next page
        next_page_token = playlist_response.get('nextPageToken')
        if not next_page_token:
            break

    return video_ids

# Example
channel_id = 'UCQ6WkI3b0rDQrGB4-Dm4Zxw' # World Bank's Channel ID
video_ids = get_all_video_ids(channel_id)

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