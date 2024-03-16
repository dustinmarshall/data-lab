import pandas as pd

import ast

# Load the dataset
df = pd.read_csv('data/wb_ag_usecases.csv')

# Extract the unique organizations from the 'implementer' column
unique_organizations = df['organization'].unique().tolist()
unique_organizations

# Extract the unique regions from the 'region' column
unique_regions = df['region'].unique().tolist()
unique_regions

# Extract the unique years from the 'years' column
df['year'] = df['year'].apply(ast.literal_eval)
unique_year = df['year'].explode().unique().tolist()
unique_year

# Extract the unique sectors from the lists of sectors in the 'sectors' column
df['sector'] = df['sector'].apply(ast.literal_eval)
unique_sector = df['sector'].explode().unique().tolist()
unique_sector

# Extract the unique countries from the 'country' column
unique_countries = df['country'].unique().tolist()
unique_countries