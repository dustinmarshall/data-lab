import os
import pandas as pd
import requests
from tqdm import tqdm
import numpy as np

# Function to create wb_ag_projects_df from WB Projects and Documents API
def create_projects_df(filename):

    # import csv file as dataframe
    df = pd.read_csv(f'data_pipelines/data/{filename}.csv')
    
    print("filling out df using WB Projects API...")
    for index, row in tqdm(df.iterrows(), total=df.shape[0]):
        project = requests.get(f"https://search.worldbank.org/api/v2/projects?format=json&fl=*&id={row['id']}").json()['projects']
        if len(project) > 0:
            for key, value in project[row['id']].items():
                print(key)
                if key == "regionname":
                    if 'region' not in df.columns:
                        df['region'] = np.nan
                    df.at[index, "region"] = value
                elif key == "countryname":
                    if 'country' not in df.columns:
                        df['country'] = np.nan
                    df.at[index, "country"] = value[0]
                elif key == "project_name":
                    if 'project' not in df.columns:
                        df['project'] = np.nan
                    df.at[index, "project"] = value
                elif key == "team_lead_details":
                    if 'contact' not in df.columns:
                        df['contact'] = np.nan
                    df.at[index, "contact"] = value[0]
                elif key == "borrower":
                    if 'organization' not in df.columns:
                        df['organization'] = np.nan
                    df.at[index, "organization"] = value
                elif key == "fiscalyear":
                    if 'year' not in df.columns:
                        df['year'] = np.nan
                    df.at[index, "year"] = value
                elif key == "sector1":
                    if 'topic' not in df.columns:
                        df['topic'] = np.nan
                    df.at[index, "topic"] = value["Name"]
        else:
            df.drop(index, inplace=True)
    
    print("adding project docs to df using WB Documents API...")
    df['document'] = None
    for index, row in tqdm(df.iterrows(), total=df.shape[0]):
        df.at[index, 'document'] = {}
        response = requests.get(f"https://search.worldbank.org/api/v2/wds?format=json&fl=pdfurl,docty&proid={row['id']}").json()
        if response:
            for doc in reversed(response['documents'].values()):
                if 'docty' in doc and 'pdfurl' in doc:
                    doctype = doc['docty']
                    pdfurl = doc['pdfurl']
                    df.at[index, 'document'][doctype] = pdfurl

    print("saving df to csv.....")
    df.to_csv(f'data_pipelines/data/{filename}.csv', index=False)

# Run the function on the _projects.csv files
create_projects_df('dddag_projects')
create_projects_df('marieagnes_projects')
