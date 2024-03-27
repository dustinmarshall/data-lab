### GENERATE PINECONE VECTOR DATABASE AND EMBEDDINGS FOR USE CASES ###

# Import libraries
import os
import csv
from tqdm import tqdm
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
import time
import ast
from settings import (
    OPENAI_API_KEY,
    PINECONE_API_KEY,
)

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Initialize Pinecone client
pc = Pinecone(api_key=PINECONE_API_KEY)

# Delete the index
print("Deleting the index...")
pc.delete_index("agrifooddatalab-index")

# Create the index
print("Creating the index...")
pc.create_index(
    name="agrifooddatalab-index",
    dimension=1536,
    metric="cosine",
    spec=ServerlessSpec(
        cloud='aws', 
        region='us-west-2'
    ) 
) 

# Connect to the index
index = pc.Index("agrifooddatalab-index")

# Function to get embeddings
def get_embedding(text, model="text-embedding-3-small"):
    try:
        return client.embeddings.create(input=[text], model=model).data[0].embedding
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
# Load wb_ag_ext_usecases.csv file
dirname = os.getcwd()
file_path = os.path.join(dirname, 'data/wb_ag_usecases.csv')

with open(file_path, mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for i, entry in enumerate(tqdm(list(reader)[:50], desc="Processing use case examples...")):
        # Extracting the text
        embedding_text = f"Title: {entry['use_case']}.\nDescription: {entry['description']}"
        # Get the embedding
        embedding = get_embedding(embedding_text)

        # Try to upsert up to three times with a wait time between retries
        max_retries = 3
        wait_time = 5  # wait time in seconds

        # generate the use case id, starting with U00001
        use_case_id = "U" + f'{i+1:05}'
                
        for attempt in range(1, max_retries + 1):
            try:
                # Insert the embedding into the index
                index.upsert([
                    (
                        use_case_id, 
                        embedding, 
                        {
                            'title': entry['use_case'],
                            'description': entry['description'],
                            'type': 'use case',
                            'project': entry['project'],
                            'organization': entry['organization'],
                            'region': entry['region'],
                            'country': entry['country'],
                            'document': ast.literal_eval(entry['document']),
                            'topic': ast.literal_eval(entry['topic']),
                            'year': ast.literal_eval(entry['year']),
                            'contact': ast.literal_eval(entry['contact']),
                            'project_id': entry['id'],
                        }
                    )
                ])
                break  # If upsert is successful, break out of the retry loop
            except Exception as e:
                print(f"Attempt {attempt} failed: {e}")
                if attempt < max_retries:
                    print(f"Waiting for {wait_time} seconds before retrying...")
                    time.sleep(wait_time)
                else:
                    print("Max retries reached. Moving to the next item.")
             
# Load wb_ag_ext_papers.csv file       
file_path = os.path.join(dirname, 'data/wb_ag_ext_papers.csv')

with open(file_path, mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for entry in tqdm(list(reader)[:25], desc="Processing learning materials..."):
        # Extracting the text
        embedding_text = f"Title: {entry['document']}.\nDescription: {entry['abstract']}"
        # Get the embedding
        embedding = get_embedding(embedding_text)

        # Try to upsert up to three times with a wait time between retries
        max_retries = 3
        wait_time = 5  # wait time in seconds

        for attempt in range(1, max_retries + 1):
            try:
                # Insert the embedding into the index
                index.upsert([
                    (
                        entry['id'], 
                        embedding, 
                        {
                            'title': entry['document'],
                            'description': entry['abstract'],
                            'type': 'learning',
                            'date': entry['date'],
                            'contact': ast.literal_eval(entry['contact']),
                            'topic': ast.literal_eval(entry['topic']),
                            'organization': entry['organization'],
                            'url': entry['url']
                        }
                    )
                ])
                break  # If upsert is successful, break out of the retry loop
            except Exception as e:
                print(f"Attempt {attempt} failed: {e}")
                if attempt < max_retries:
                    print(f"Waiting for {wait_time} seconds before retrying...")
                    time.sleep(wait_time)
                else:
                    print("Max retries reached. Moving to the next item.")
                    
# Load wb_ag_ext_datasets.csv file       
file_path = os.path.join(dirname, 'data/wb_ag_datasets.csv')

with open(file_path, mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for entry in tqdm(list(reader)[:25], desc="Processing datasets..."):
        # Extracting the text
        embedding_text = f"Title: {entry['name']}.\nDescription: {entry['description']}"
        # Get the embedding
        embedding = get_embedding(embedding_text)

        # Try to upsert up to three times with a wait time between retries
        max_retries = 3
        wait_time = 5  # wait time in seconds

        for attempt in range(1, max_retries + 1):
            try:
                # Insert the embedding into the index
                index.upsert([
                    (
                        entry['dataset_id'], 
                        embedding, 
                        {
                            'title': entry['name'],
                            'description': entry['description'],
                            'type': 'dataset',
                            'project_id': entry['project_id'],
                            'file': ast.literal_eval(entry['file'])
                        }
                    )
                ])
                break  # If upsert is successful, break out of the retry loop
            except Exception as e:
                print(f"Attempt {attempt} failed: {e}")
                if attempt < max_retries:
                    print(f"Waiting for {wait_time} seconds before retrying...")
                    time.sleep(wait_time)
                else:
                    print("Max retries reached. Moving to the next item.")

# Example: Querying the index
# query_result = index.query(queries=[[0.1, 0.2, ..., 0.128]], top_k=5)

# Remember to delete the index if it is no longer needed
#pinecone.delete_index(index_name)