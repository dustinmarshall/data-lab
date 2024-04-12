from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI
import os
from tqdm import tqdm
from settings import (OPENAI_API_KEY, YOUTUBE_API_KEY)
import json

# Function to get video description
def get_video_description(video_id):
    # Build the YouTube API client
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
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
    # Try to fetch video details
    try:
        response = youtube.videos().list(
            part='snippet',
            id=video_id
        ).execute()
        # Check if the video exists and has a snippet
        if not response['items']:
            print("Video not found.")
            return None
        video_details = response['items'][0]['snippet']
        # Return the description
        return video_details['description']
    except Exception as e:
        print(f"Error occurred: {e}")
        return None

# Function to get all video ids from a channel
def get_all_video_ids(channel_id):
    # Initialize list
    video_ids = []
    # Get the channel's content details
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
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

# Function to get summary text
def get_summary(text):
    client = OpenAI(
        api_key=OPENAI_API_KEY,
    )
    if not isinstance(text, str):
        print("Error: Text must be a string")
        return None
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Summarize the following text in 40 tokens or less using the framing, 'A recording of a webinar from the World Bank's Data Driven Digital Agriculture YouTube channel detailing {summary}'"},
                {"role": "user", "content": text}
            ]
        )
        # Accessing the text in the correct format
        return response.choices[0].message.content  # Adjusted to access .text attribute and strip any extra whitespace
    except Exception as e:
        print("An error occurred:", e)
        return None

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
    # Build the YouTube API client
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
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

# Get all video ids from the World Bank's Data Driven Digital Agriculture YouTube channel
channel_id = 'UCQ6WkI3b0rDQrGB4-Dm4Zxw'
video_ids = get_all_video_ids(channel_id)

# generate the transcripts list
transcripts_list = []
for id in tqdm(video_ids):
    transcript_list = get_video_transcript(id)
    if transcript_list:
        transcripts_list += transcript_list

# Saving the list to a new JSON file
dirname = os.getcwd()
output_file_path = os.path.join(dirname, 'data_pipelines/data/wb_youtube_videos.json')

with open(output_file_path, 'w') as output_file:
    json.dump(transcripts_list, output_file, indent=4)