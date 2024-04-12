import pandas as pd
from openai import OpenAI
import json
import requests
import os
import ast
import time
from settings import (OPENAI_API_KEY)

csv_input = 'data_pipelines/data/marieagnes_projects.csv'
csv_output = 'data_pipelines/data/marieagnes_usecases.csv'

# Initialize OpenAI client
client = OpenAI(
    api_key=OPENAI_API_KEY,
)

# Function to submit tool outputs
def submit_tool_outputs(thread_id, run_id, tool_call_id, output):
    client.beta.threads.runs.submit_tool_outputs(
        thread_id=thread_id,
        run_id=run_id,
        tool_outputs=[{
            "tool_call_id": tool_call_id,
            "output": json.dumps(output)
        }]
    )

# Function to process a document and update the DataFrame
def process_document(url, id, project, organization, region, country, document, topic, year, contact):

    # Read wb_use_case_summaries.csv into wb_use_case_summaries_df
    if os.path.exists(csv_output):
        use_cases_df = pd.read_csv(csv_output)
    else:
        use_cases_df = pd.DataFrame(columns=['id', 'use_case', 'project', 'description', 'organization', 'region', 'country', 'document', 'topic', 'year', 'contact'])

    # Download the file
    response = requests.get(url)
    file_name = 'downloaded_file.pdf'
    with open(file_name, 'wb') as file:
        file.write(response.content)

    # Initialize OpenAI client
    client = OpenAI(api_key=OPENAI_API_KEY)

    # Upload the file to OpenAI
    print("Uploading files...")
    file_path = file_name
    project_document_file = client.files.create(
      file=open(file_path, "rb"),
      purpose='assistants'
    )
    
    # Initialize tools
    tools = [
        {
            "type": "retrieval"
        }
    ]

    # Function mapping
    function_mapping = {
    }
    
    # Create the Assistant
    print("Creating Assistant...")
    assistant = client.beta.assistants.create(
        name="Use Case Summarizer",
        instructions=
            '''
            Role: 
            In your knowledge base is a pdf file detailing an agricultural project. Your job is to identify the distinct methodologies that
            the project leverages to implement the project, then produce a summary of each methodology (framing the methodology as a 
            use case example) in alignment with the provided template. The goal is to produce use case examples that can be used by other 
            teams in their own projects.

            Instructions:
            - Review the document in your knowledge base and identify the distinct methodologies that the project leverages.
            - For each, generate a 200 word description and 5-10 word title detailing how the use case example was implemented.
            - Return the title and description in a JSON array, with no additional text before or after.
            - Ensure that the description is actually 200 words and the title is actually 5-10 words.
            - Even if methodologies aren't explicitly mentioned, do your best to deduce them, otherwise return an empty JSON array.
            
            Template:
            [
                {
                    "use_case": "Title of use case example 1",
                    "description": "Description of use case example 1"
                },
                {
                    "use_case": "Title of use case example 2",
                    "description": "Description of use case example 2"
                }
            ]
            ''',
        model="gpt-4-0125-preview",
        tools = tools,
        file_ids=[project_document_file.id]
    )

    # Create a thread
    print("Creating thread...")
    thread = client.beta.threads.create(
    )

    # Add message to the thread
    print("Adding message to the thread...")
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content= ""
    )

    # Run the Assistant
    print("Running the Assistant...")
    run = client.beta.threads.runs.create(
        thread_id=thread.id, 
        assistant_id=assistant.id,
        instructions=""
    )

    # Handle tool outputs
    while run.status != 'completed':
        time.sleep(10)
        
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        
        # Print the run status
        print(f"Run status: {run.status}")
        
        # If the run is failed, retry
        if run.status == "failed":
            print("Run failed:", run.last_error)
            break

        # Handle the run status
        if run.status == "requires_action":
            print("Action required by the assistant...")
            for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                if tool_call.type == "function":
                    function_name = tool_call.function.name
                    print(f"Function name: {function_name}")
                    arguments = json.loads(tool_call.function.arguments)
                    print(f"Arguments: {arguments}")
                    if function_name in function_mapping:
                        print(f"Calling function {function_name}...")
                        response = function_mapping[function_name](**arguments)
                        submit_tool_outputs(thread.id, run.id, tool_call.id, response)

    # Fetch the Assistant's response  
    print("Fetching Assistant's response...")
    reply = client.beta.threads.messages.list(
        thread_id=thread.id
    )
    messages = reply.data

    assistant_reply = ""
    for message in messages:
        if message.role == "assistant":
            for content in message.content:
                if content.type == "text":
                    assistant_reply = content.text.value
                    print("assistant_reply: ", assistant_reply, "type: ", type(assistant_reply))
                    # Find the position of the first '[' and the last ']'
                    start_index = assistant_reply.find('[')
                    end_index = assistant_reply.rfind(']')

                    # Extract the substring between these positions
                    if start_index != -1 and end_index != -1:
                        json_string = assistant_reply[start_index:end_index+1]
                        try:
                            formatted_assistant_reply = json.loads(json_string)
                            print("formatted_assistant_reply: ", formatted_assistant_reply, "type: ", type(formatted_assistant_reply))
                        except json.JSONDecodeError as e:
                            print("Failed to decode JSON. Error: ", e)
                    else:
                        print("The string does not contain a valid JSON structure.")

                    break
            if assistant_reply:
                break
    
    # Process the Assistant's response
    for use_case in formatted_assistant_reply:
        
        print("use case: ", use_case, "type: ", type(use_case))
        
        # Check if the use_case is a string and convert it to a dictionary
        if isinstance(use_case, str):
            use_case = ast.literal_eval(use_case)
        
        # Add additional fields to the use_case
        use_case['id'] = id
        use_case['project'] = project
        use_case['organization'] = organization
        use_case['region'] = region
        use_case['country'] = country
        use_case['document'] = document
        use_case['topic'] = topic
        use_case['year'] = year
        use_case['contact'] = contact

        # Add new row to DataFrame
        use_cases_df = pd.concat([use_cases_df, pd.DataFrame([use_case])], ignore_index=True)

        # Write the updated DataFrame to CSV
        use_cases_df.to_csv(csv_output, index=False)

    # Delete the file locally
    if os.path.exists(file_name):
        os.remove(file_name)
    else:
        print("The file does not exist")
        
    ## Delete the file object
    #client.beta.assistants.files.delete(
    #    file_id=project_document_file.id,
    #    assistant_id=assistant.id
    #)
        
    ## Delete the assistant
    #client.beta.assistants.delete(
    #    assistant_id=assistant.id
    #)

# Read wb_ag_projects.csv into wb_ag_projects_df
projects_df = pd.read_csv(csv_input)

# Read wb_use_case_summaries.csv into wb_use_case_summaries_df
if os.path.exists(csv_output):
    use_cases_df = pd.read_csv(csv_output)
else:
    use_cases_df = pd.DataFrame(columns=['id', 'use_case', 'project', 'description', 'organization', 'region', 'country', 'document', 'topic', 'year', 'contact'])

# iterate through projects df and process each document
for index, row in projects_df.iterrows():
    if not use_cases_df['id'].isin([row['id']]).any():
        # Check if projectdocs is a string and convert it to a dictionary
        if isinstance(row['document'], str):
            try:
                document = ast.literal_eval(row['document'])
            except ValueError:
                # Handle the exception if the string cannot be converted to a dictionary
                continue
        for doctype, url in document.items():
            if doctype == 'Project Appraisal Document' or doctype == 'Project Paper' or doctype == 'Implementation Completion and Results Report' or doctype == 'Implementation Completion Report Review': 
                print("Processing document: ", doctype, " for project: ", row['id'])
                process_document(url, row['id'], row['project'], row['organization'], row['region'], row['country'], row['document'], row['topic'], row['year'], row['contact'])
                #time.sleep(300)
                break
            elif doctype == 'Project Information Document':
                print("Processing document: ", doctype, " for project: ", row['id'])
                process_document(url, row['id'], row['project'], row['organization'], row['region'], row['country'], row['document'], row['topic'], row['year'], row['contact'])
                #time.sleep(300)
                break
            else:
                continue