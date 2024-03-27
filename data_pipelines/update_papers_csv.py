### ADD PDF URLS TO wb_ag_ext_projects.csv FILE ###

import requests
import pandas as pd
from tqdm import tqdm
import os

# Load the CSV file
dirname = os.getcwd()
print(dirname)
file_path = os.path.join(dirname, 'data_pipelines/data/wb_ag_papers.csv')
print(file_path)
df = pd.read_csv(file_path)

# Loop through the DataFrame and update the URL column
for index, row in tqdm(df.iterrows(), total=df.shape[0]):
    id_value = row['Report No.']
    api_call = f"https://search.worldbank.org/api/v2/wds?fl=pdfurl&repnb={id_value}"
    response = requests.get(api_call)
    try:
        pdfurl = next(iter(response.json()['documents'].values()))['pdfurl']
        df.at[index, 'url'] = pdfurl
    except:
        # delete row if no pdfurl found
        df.drop(index, inplace=True)
    
    # Save the updated DataFrame to a new CSV file
    df.to_csv('data_pipelines/data/wb_ag_papers_withurl.csv', index=False)