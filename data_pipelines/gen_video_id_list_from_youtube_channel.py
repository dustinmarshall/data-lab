from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI
from dotenv import load_dotenv
import os
from tqdm import tqdm
import pandas as pd

# Function to get summary text
def get_summary(text):
    # Load api key from env
    api_key = os.getenv("OPENAI_API_KEY")

    client = OpenAI(
        api_key=api_key,
    )
    
    if not isinstance(text, str):
        print("Error: Text must be a string")
        return None

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Model can be changed if needed
            messages=[
                {"role": "system", "content": "Summarize the following text in 40 tokens or less using the framing, 'A video on the World Bank's YouTube channel detailing {summary}'"},
                {"role": "user", "content": text}
            ]
        )
        # Accessing the text in the correct format
        return response.choices[0].message.content  # Adjusted to access .text attribute and strip any extra whitespace
    except Exception as e:
        print("An error occurred:", e)
        return None

# Function to get video description
def get_video_description(video_id):
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
    # Load api key from env
    load_dotenv()
    api_key = os.getenv("YOUTUBE_API_KEY")

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
        
        # Check if there is a next page
        next_page_token = playlist_response.get('nextPageToken')
        if not next_page_token:
            break

    return video_ids

# Example
channel_id = 'UCE9mrcoX-oE-2f1BL-iPPoQ' # World Bank's Channel ID
video_ids = get_all_video_ids(channel_id)