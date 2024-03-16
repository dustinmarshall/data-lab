### GENERATE DATASETS FILE ###

import requests
from tqdm import tqdm
import csv
import json
import os

def is_related_to_food_or_agriculture(description):
    keywords = {
    'food', 'agriculture', 'farming', 'crops', 'livestock', 'harvest', 
    'horticulture', 'irrigation', 'fertilizer', 'farm', 'ranch', 'grain',
    'vegetable', 'fruit', 'meat', 'dairy', 'poultry', 'aquaculture', 'agronomy',
    'food security', 'rural development', 'agricultural economics', 'sustainable agriculture',
    'agricultural policy', 'land use', 'agricultural trade', 'food supply', 'agroecology',
    'agribusiness', 'agricultural technology', 'agricultural finance', 'agricultural investment',
    'crop rotation', 'soil management', 'pest management', 'agricultural research', 'agricultural extension',
    'food processing', 'food distribution', 'market access', 'subsistence agriculture', 'commercial agriculture',
    'agricultural productivity', 'nutrition', 'food aid', 'agricultural innovation', 'climate change and agriculture',
    'agricultural insurance', 'rural livelihoods', 'agricultural workers', 'agricultural supply chain',
    'biofortification', 'food policy', 'agricultural sustainability', 'agroforestry'
    }

    if description is None:
        return False

    description_lower = description.lower()
    for keyword in keywords:
        if keyword in description_lower:
            return True

    return False

dirname = os.getcwd()
file_path = os.path.join(dirname, 'data/wb_datasets.json')

with open(file_path, 'r') as file:
    data = json.load(file)

datasets = data['data']
base_url = 'https://datacatalogapi.worldbank.org/ddhxext/DatasetView?dataset_unique_id='
simplified_datasets = []

for dataset in tqdm(datasets, desc="Processing datasets"):
    if dataset.get('source') == "MICRODATA":
        continue
    dataset_id = dataset.get('dataset_unique_id')
    url = base_url + dataset_id
    response = requests.get(url)
    response_data = response.json()
    name = response_data.get('name', 'None')
    description = response_data.get('identification', {}).get('description', 'None')

    if not is_related_to_food_or_agriculture(description):
        continue

    project_id = response_data.get('identification', {}).get('wb_project_reference', 'None')
    resources = response_data.get('Resources', 'None')
    
    files = []
    if resources != 'None':
        for resource in resources:
            file = {
                'name': resource.get('name', 'None'),
                'description': resource.get('description', 'None'),
                'url': resource.get('url', 'None')
            }
            files.append(file)

    simplified_dataset = {
        'name': name,
        'description': description,
        'dataset_id': dataset_id,
        'project_id': project_id,
        'files': json.dumps(files)  # Convert list of files to a JSON string
    }
    simplified_datasets.append(simplified_dataset)

output_file_path = os.path.join(dirname, 'data/wb_ag_datasets.csv')
with open(output_file_path, mode='w', newline='', encoding='utf-8') as output_file:
    writer = csv.DictWriter(output_file, fieldnames=['name', 'description', 'dataset_id', 'project_id', 'files'])
    writer.writeheader()
    for dataset in simplified_datasets:
        writer.writerow(dataset)