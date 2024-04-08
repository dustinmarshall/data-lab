from openai import OpenAI
import streamlit as st
import time
import ast
from pinecone import Pinecone
import json
import requests
from settings import (
    OPENAI_API_KEY,
    PINECONE_API_KEY,
    PINECONE_INDEX,
    PINECONE_ENVIRONMENT,
    EMBEDDING_MODEL,
    LLM_MODEL,
    REGIONS,
    COUNTRIES,
    YEARS,
    TYPES,
    ORGANIZATIONS,
    TOPICS,
)

# Set up Streamlit page title and subheader
st.title("AgriFood Data Lab")
st.subheader("Discover agricultural learning, use case, and dataset resources, with AI-enabled search, retrieval, and analysis capabilities.")
st.markdown("---")

# Initialize OpenAI and Pinecone clients
client = OpenAI(api_key=OPENAI_API_KEY)
pc = Pinecone(
    api_key=PINECONE_API_KEY, 
    environment=PINECONE_ENVIRONMENT,
)

# Connect to Pinecone index
index = pc.Index(PINECONE_INDEX)

# Load the AgriFood Data Lab logo and its black version 
image_path = "images/logo.png"
with open(image_path, "rb") as file:
    img_bytes = file.read()
image_path_black = "images/logo_black.png"
with open(image_path_black, "rb") as file:
    img_bytes_black = file.read()
    
# Set up Streamlit button persistence
# https://docs.streamlit.io/library/advanced-features/button-behavior-and-examples
if 'clicked' not in st.session_state:
    st.session_state.clicked = False
def click_button():
    st.session_state.clicked = True

# Define function to call Embedding API and return embedding
def get_embedding(text, model=EMBEDDING_MODEL):
    try:
        return client.embeddings.create(input=[text], model=model).data[0].embedding
    except Exception as e:
        st.error(f"Failed to get embedding: {e}")
        # Optionally, log the error for debugging purposes
        print(f"Error getting embedding for text: {text}. Error: {e}")
        return None

# Function to download file and upload to OpenAI assistant
def download_file_upload_to_assistant(id):
    
    # Get the file URL from Pinecone
    file = index.fetch([id])
    url = file.vectors[id].metadata["url"]
    
    # Download the file
    with st.spinner(text="Downloading file..."):
        try:
            response = requests.get(url)
            with open('downloaded_file.pdf', 'wb') as file:
                file.write(response.content)
        except Exception as e:
            print("Error:", e)

    # Upload the file to OpenAI
    with st.spinner(text="Uploading file..."):
        try:
            client.files.create(
                file=open('downloaded_file.pdf', "rb"),
                purpose='assistants'
            )
        except Exception as e:
            print("Error:", e)

# Define function to generate streamed text response from string
# https://docs.streamlit.io/knowledge-base/tutorials/build-conversational-apps
def response_generator(text):
    for segment in text.split('\n'):
        print(segment)
        for word in segment.split():
            yield word + " "
            time.sleep(0.075)
        yield '  \n'
        time.sleep(0.05)

# Define function to preselect search filters based on the message history
def preselect_search_filters(type=[], year=[], country=[], region=[], organization=[], topic=[]):
    global st
    st.session_state.type = type
    st.session_state.year = year
    st.session_state.country = country
    st.session_state.region = region
    st.session_state.organization = organization
    st.session_state.topic = topic
    col1, col2, col3 = st.columns(3)
    with col1:
        st.session_state.type = st.multiselect(
            'Type(s)',
            TYPES,
            st.session_state.type
        )                
        st.session_state.year = st.multiselect(
            'Year(s)',
            YEARS,
            st.session_state.year
        )
    with col2:
        st.session_state.country = st.multiselect(
            'Country(s)',
            COUNTRIES,
            st.session_state.country
        )
        st.session_state.region = st.multiselect(
            'Region(s)',
            REGIONS,
            st.session_state.region
        )
    with col3:
        st.session_state.organization = st.multiselect(
            'Organization(s)',
            ORGANIZATIONS,
            st.session_state.organization
        )
        st.session_state.topic = st.multiselect(
            'Topic(s)',
            TOPICS,
            st.session_state.topic
        )

# Define function to search the knowledge base using a query and selected filters
def search_knowledge_base(query, type, year, country, region, organization, topic):
    # Get the embedding of the query
    embedding = get_embedding(query)
    # generate the filter dictionary
    filter_dict = {}
    if type is not []:
        filter_dict["type"] = {"$in": type}
    if year is not []:
        filter_dict["year"] = {"$in": year}
    if country is not []:
        filter_dict["country"] = {"$in": country}
    if region is not []:
        filter_dict["region"] = {"$in": region}
    if organization is not []:
        filter_dict["organization"] = {"$in": organization}
    if topic is not []:
        filter_dict["topic"] = {"$in": topic}
    # Query the knowledge base index
    try:
        top_k_matches = index.query(
            top_k=5,
            include_metadata=True,
            include_values=False,
            vector=embedding
        )
    except Exception as e:
        st.error("Failed to query the Pinecone index. Please try again later.")
        print(f"Error querying Pinecone index: {e}")
        return {"matches": []}
    # Extract the right metadata from the top k matches
    match_string = "We used the conversation and selected filters to run an AI-enabled semantic search on our database. Here are the top matches:"
    for match in top_k_matches['matches']:
        metadata = match['metadata']
        match_string += f"  \n  \n**{metadata['title']} in {metadata['country']}:**  {metadata['description'][:metadata['description'].find('.')+1]} (ID: {match['id']})  \n  \n"
    match_string += "Would you like to know more about any of these matches or search for something else?"
    # Return the top k matches
    return match_string

# Define function to get more information on a record from the knowledge base using its id
def get_more_information(id):
    # Get the metadata of the record from the knowledge base
    key = list(index.fetch(ids=[id])['vectors'])[0]
    metadata = index.fetch(ids=[id])['vectors'][key]['metadata']
    # Format metadata into markdown string
    documents = {}
    for doc in metadata['document']:
        doc = ast.literal_eval('{' + doc + '}')
        documents.update(doc)
    documents_string = ""
    for key, value in documents.items():
        documents_string += f" - [{key}]({value})  \n"
    # convert list of strings into comma-seperated string
    markdown_string = f"Here's all of the information we have on that record in our database:  \n  \n**Title:** {metadata['title']}  \n **Description:** {metadata['description']}  \n **Type:** use case  \n **Project:** {metadata['project']}  \n **Organization:** {metadata['organization']}  \n **Region:** {metadata['region']}  \n **Country:** {metadata['country']}  \n**Document(s):** {documents_string}  \n **Topic(s):** {', '.join(metadata['topic'])}  \n **Year(s):** {', '.join(metadata['year'])}  \n **Contact(s):** {', '.join(metadata['contact'])}  \n **Project ID:** {metadata['project_id']}  \n  \nWould you like use to analyze any of the linked files or search for something else?"
    return markdown_string

functions = {
    "preselect_search_filters": preselect_search_filters,
    "get_more_information": get_more_information
}

# Define function to execute function call and return results
def call_tool(tool_call, functions):
    # Extract the function name and arguments from the message
    function_name = tool_call.function.name
    function_args = json.loads(tool_call.function.arguments)
    # Check if the function exists
    if function_name in functions:
        # Call the function with the provided arguments
        results = functions[function_name](**function_args)
    else:
        results = f"Error: function {function_name} does not exist"
    return results

# Define function to call Chat Completion API with function and return response
def chat_completion_with_function(messages, tools, tool_choice, model, functions):
    # Try to call Chat Completion API to generate response
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
        )
    except Exception as e:
        print("Unable to generate Chat Completion response")
        print(f"Exception: {e}")
        return e
    # Extract the response message
    tool_calls = response.choices[0].message.tool_calls
    # Check if the response message requires a function call
    if tool_calls == []:
        print(f"Tool not required, responding to user")
        return response
    else:
        print(f"Tool requested, calling function")
        # Extract the function name and arguments from the message
        function_name = tool_calls[0].function.name
        function_args = json.loads(tool_calls[0].function.arguments)
        # Check if the function exists
        if function_name in functions:
            # Call the function with the provided arguments
            results = functions[function_name](**function_args)
        else:
            results = f"Error: function {function_name} does not exist"
        return results

# Define the tools to be used in the conversation
tools = [
    {
        "type": "function",
        "function": {
            "name": "preselect_search_filters",
            "description": "Preselect search filters based on the message history.",
            "parameters": {
                "type": 
                    "object",
                "properties": {
                    "type": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": f"""
                            Resource type(s). Options include:
                            {TYPES}
                        """
                    },
                    "year": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": f"""
                            The year(s) that the learning/use case/dataset covers. Options include:
                            {YEARS}
                        """
                    },
                    "country": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": f"""
                            The country(s) involved. Options include:
                            {COUNTRIES}
                        """
                    },
                    "region": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": f"""
                            The region(s) involved. Options include:
                            {REGIONS}
                        """
                    },
                    "organization": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": f"""
                            The organization(s) involved. Options include:
                            {ORGANIZATIONS}
                        """
                    },
                    "topic": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": f"""
                            The agricultural topic(s) involved. Options include:
                            {TOPICS}
                        """
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_more_information",
            "description": "Get more information on a record from the knowledge base using its id.",
            "parameters": {
                "type": 
                    "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "The id of the record to retrieve."
                    },
                },
                "required": [
                    "id"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "download_file_upload_to_assistant",
            "description": "Download a file and upload it to the assistant for retrieval or code interpreter.",
            "parameters": {
                "type": 
                    "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "The id of the file to download."
                    }
                },
                "required": [
                    "id"
                ]
            }
        }
    }
]

# Define the tools to be used by the assistant in the conversation
assistant_tools = [
    {
        "type": "code_interpreter"
    },
    {
        "type": "retrieval",
    }
]

# Initialize Streamlit chat display
if "messages" not in st.session_state:
    # Initialize the chat messages
    st.session_state.messages = []
    # Add the assistant welcome message
    st.session_state.messages.append(
        {
            "role": "assistant", 
            "content": "Welcome to the AgriFood Data Lab!  \n  \nExplore agricultural use cases, datasets, and learning resources, with AI-enabled search, retrieval, and analysis capabilities.  \n  \nHow can we help you today?"
        }
    )
    # Display the assistant welcome message
    with st.chat_message(name="assistant", avatar=img_bytes):
        st.write_stream(
            response_generator(
                "Welcome to the AgriFood Data Lab!  \n  \nExplore agricultural use cases, datasets, and learning resources, with AI-enabled search, retrieval, and analysis capabilities.  \n  \nHow can we help you today?"
            )
        )

# Rerun the Streamlit chat if already initialized
elif "messages" in st.session_state:
    for message in st.session_state.messages: 
        # Redisplay the user and assistant chat messages (without streaming effect)
        if message["role"] == "assistant":
            with st.chat_message(name="assistant", avatar=img_bytes):
                st.write(message["content"])
            # Redisplay the filters if the assistant message is about preselecting search filters
            if message["content"] == "Thank you. We've added some optional filters that you can edit to help us narrow down your search.":
                with st.chat_message(name="user", avatar=img_bytes_black):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.multiselect(
                            'Type(s)',
                            TYPES,
                            st.session_state.type
                        )                
                        st.multiselect(
                            'Year(s)',
                            YEARS,
                            st.session_state.year
                        )
                    with col2:
                        st.multiselect(
                            'Country(s)',
                            COUNTRIES,
                            st.session_state.country
                        )
                        st.multiselect(
                            'Region(s)',
                            REGIONS,
                            st.session_state.region
                        )
                    with col3:
                        st.multiselect(
                            'Organization(s)',
                            ORGANIZATIONS,
                            st.session_state.organization
                        )
                        st.multiselect(
                            'Topic(s)',
                            TOPICS,
                            st.session_state.topic
                        )
                    # Redisplay (persistent) search button that triggers the assistant response
                    st.button("Search", on_click=click_button)
        else:
            with st.chat_message(name="user", avatar=img_bytes_black):            
                st.write(message["content"])                    

# Add Streamlit chat user input
if prompt := st.chat_input("Type your reply here..."):
    # Add the user message to the chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display the user message
    with st.chat_message("user", avatar=img_bytes_black):
        st.write(prompt)

# Add Streamlit chat assistant response asking for more details
if len(st.session_state.messages) == 2 and st.session_state.messages[-2]["content"] == "Welcome to the AgriFood Data Lab!  \n  \nExplore agricultural use cases, datasets, and learning resources, with AI-enabled search, retrieval, and analysis capabilities.  \n  \nHow can we help you today?":
    # Add the assistant message to the chat history
    st.session_state.messages.append(
        {
            "role": "assistant", 
            "content": "Could you describe what you're looking for to us in more detail?"
        }
    )
    # Display the assistant message (with streaming effect)
    with st.chat_message("assistant", avatar=img_bytes):
            st.write(
                response_generator(
                    "Could you describe what you're looking for to us in more detail?"
                )
            )

# Add Streamlit chat assistant response preselecting search filters
elif len(st.session_state.messages) == 4 and st.session_state.messages[-2]["content"] == "Could you describe what you're looking for to us in more detail?":
    # Add the assistant message to the chat history
    st.session_state.messages.append(
        {
            "role": "assistant", 
            "content": "Thank you. We've added some optional filters that you can edit to help us narrow down your search."
        }
    )
    # Display the assistant message (with streaming effect)
    with st.chat_message("assistant", avatar=img_bytes):
        st.write_stream(
            response_generator(
                "Thank you. We've added some optional filters that you can edit to help us narrow down your search."
            )
        )
    # Display the search filters for the user to edit and submit
    with st.chat_message("user", avatar=img_bytes_black):
        with st.spinner("Generating filters..."):
            # Insert the system prompt to the chat history
            st.session_state.messages.insert(0, {
                    "role": "system", 
                    "content": "Use the conversation to call the preselect function."
                })
            # Call the Chat Completion with function function
            response = chat_completion_with_function(
                st.session_state.messages, 
                tools=tools, 
                tool_choice='auto', 
                model=LLM_MODEL,
                functions=functions)
            # Remove the system prompt from the chat history
            st.session_state.messages.pop(0)
            # Add a (persistent) search button that triggers the assistant response
            st.button("Search", on_click=click_button)

# Add Streamlit chat assistant response with search results
elif len(st.session_state.messages) == 5 and st.session_state.clicked and st.session_state.messages[-3]["content"] == "Could you describe what you're looking for to us in more detail?":
    # Add the assistant message to the chat history
    with st.chat_message("assistant", avatar=img_bytes):
        # Search the knowledge base using the query and selected filters (currently not using the filters, only the query)
        with st.spinner("Searching database..."):           
            match_string = search_knowledge_base(
                query=st.session_state.messages[-2]["content"],
                type=[],
                year=[],
                country=[],
                region=[],
                organization=[],
                topic=[]
            )
        # Display the matches (with streaming effect)    
        st.write_stream(
                response_generator(
                    match_string
                )
            )
        # Add the assistant message to the chat history
        st.session_state.messages.append(
            {
                "role": "assistant", 
                "content": match_string
            }
        )

# If the last message ends with the assistant asking for more details, call the get_more_information function
if len(st.session_state.messages) > 6 and st.session_state.messages[-2]["content"].endswith("else?"):
    # Insert the system prompt to the chat history
    st.session_state.messages.insert(0, {
        "role": "system", 
        "content": "Use the conversation to call the get_more_information function."
    })
    # Call Chat Completion with function function
    response = chat_completion_with_function(
        st.session_state.messages, 
        tools=tools, 
        tool_choice='auto', 
        model=LLM_MODEL,
        functions=functions)
    # Remove the system prompt from the chat history
    st.session_state.messages.pop(0)
    # Add the assistant message to the chat history
    st.session_state.messages.append(
        {
            "role": "assistant", 
            "content": response
        }
    )
    # Display the assistant message (with streaming effect)
    with st.chat_message("assistant", avatar=img_bytes):
        st.write(
            response_generator(
                response
            )
        )

# If the last message ends with the assistant asking for more details, call the get_more_information function
if len(st.session_state.messages) > 8 and st.session_state.messages[-2]["content"].endswith("else?"):
    assistant = client.beta.assistants.create(
        name="AgriFood Data Lab",
        instructions="Use the conversation history to call the ",
        model=LLM_MODEL,
    )
    
    # Add the assistant message to the chat history
    st.session_state.messages.append(
        {
            "role": "assistant", 
            "content": response
        }
    )
    # Display the assistant message (with streaming effect)
    with st.chat_message("assistant", avatar=img_bytes):
        st.write(
            response_generator(
                response
            )
        )  