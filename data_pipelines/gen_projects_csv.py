### GENERATE PROJECTS CSV FROM WORLD BANK PROJECTS API ###

# Function to create wb_ag_projects_df from WB Projects and Documents API
def create_ag_projects_df():
    
    print("creating wb_ag_projects_df from WB Projects API...")
    wb_ag_projects = requests.get('https://search.worldbank.org/api/v2/projects?rows=10000&mjsectorcode_exact=AX').json()['projects']
    wb_ag_projects_df = pd.DataFrame.from_dict(wb_ag_projects, orient='index')
    
    print("adding projectdocs from to WB Documents API wb_ag_projects_df...")
    for index, row in tqdm(wb_ag_projects_df.iterrows(), total=wb_ag_projects_df.shape[0]):
        wb_ag_projects_df.at[index, 'projectdocs'] = {}
        response = requests.get(f"https://search.worldbank.org/api/v2/wds?format=json&fl=pdfurl,docty&proid={row['id']}").json()
        if response:
            for doc in reversed(response['documents'].values()):
                if 'docty' in doc and 'pdfurl' in doc:
                    doctype = doc['docty']
                    pdfurl = doc['pdfurl']
                    wb_ag_projects_df.at[index, 'projectdocs'][doctype] = pdfurl

    print("saving wb_ag_projects_df to csv...")
    wb_ag_projects_df.to_csv('data/wb_ag_projects.csv', index=False)

# Check if wb_ag_projects.csv exists, if not create it
if not os.path.exists('data/wb_ag_projects.csv'):
    create_ag_projects_df()