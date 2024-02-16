from openai import OpenAI
import streamlit as st
import time
import random
import ast
import cohere
from pinecone import Pinecone
import json
#from tenacity import retry, wait_random_exponential, stop_after_attempt

# Set up Streamlit page title and subheader
st.title("AgriFood Data Lab")
st.subheader("Discover agricultural learning, use case, and dataset resources, with AI-enabled search, retrieval, and analysis capabilities.")
st.markdown("---")

# Initialize OpenAI and Pinecone clients
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
pc = Pinecone(api_key=st.secrets["PINECONE_API_KEY"], environment="gcp-starter")

# Initialize OpenAI models and Pinecone index
GPT_MODEL = "gpt-3.5-turbo-0125"
EMBEDDING_MODEL = "text-embedding-3-small"
PINECONE_INDEX = "agrifooddatalab-index"

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
#@retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(3))
def get_embedding(text, model=EMBEDDING_MODEL):
    return client.embeddings.create(input = [text], model=model).data[0].embedding

## Function to download file and upload to OpenAI assistant
#@retry(wait=wait_random_exponential(min=1, max=40), stop=stop_after_attempt(3))
#def download_file_upload_to_assistant(id):
#    
#    # Get the file URL from Pinecone
#    file = index.fetch([id])
#    url = file.vectors[id].metadata["url"]
#    
#    # Download the file
#    with st.spinner(text="Downloading file..."):
#        try:
#            response = requests.get(url)
#            with open('downloaded_file.pdf', 'wb') as file:
#                file.write(response.content)
#        except Exception as e:
#            print("Error:", e)
#
#    # Upload the file to OpenAI
#    with st.spinner(text="Uploading file..."):
#        try:
#            client.files.create(
#                file=open('downloaded_file.pdf', "rb"),
#                purpose='assistants'
#            )
#        except Exception as e:
#            print("Error:", e)
#    
#    # Download file from the provided URL
#    response = requests.get(url, stream=True)
#    total_size = int(response.headers.get("content-length", 0))
#    print(total_size)
#    block_size = 1024
#    
#    # Add streamlit progress bar for downloading file
#    progress_bar = st.progress(0)
#    progress_value = 0
#
#    # Create a temporary file to store the downloaded file
#    with tempfile.NamedTemporaryFile(delete=False, mode='wb') as temp_file:
#        tmp_file_path = temp_file.name  # This is the path to the temporary file
#        print(tmp_file_path)
#        for data in response.iter_content(block_size):
#            temp_file.write(data)
#            progress_value += len(data)
#            # Update the progress bar
#            progress_bar.progress(progress_value / total_size)
#        
#    # if file is zip, extract all files
#    if tmp_file_path.endswith('.zip'):
#        import zipfile
#        with zipfile.ZipFile(tmp_file_path, 'r') as zip_ref:
#            zip_ref.extractall(tmp_file_path.replace('.zip', ''))
#        tmp_file_path = tmp_file_path.replace('.zip', '')
#    
#    # Upload file to OpenAI assistant
#    with open(tmp_file_path, 'rb') as file_to_upload:
#        client.files.create(
#            file=file_to_upload,
#            purpose='assistants'
#        )

# Define function to query PineCone API and return top k matches
#@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
def query_pinecone_index(embedding, top_k=5, include_metadata=True, include_values=False):
    # Query the knowledge base index
    top_k_matches = index.query(
        top_k=top_k,
        include_metadata=include_metadata,
        include_values=include_values,
        vector=embedding
    )
    # Return the top k matches
    return top_k_matches

## Function to rerank the top 10 resources using Cohere
#@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
#def rerank_rag_matches(query, documents):
#    st.session_state['conversation'].append("**Assistant:** Reranking results...")
#    reranked_results = co.rerank(
#        query=query, 
#        documents=documents, 
#        top_n=5, 
#        model="rerank-multilingual-v2.0")
#    return reranked_results

# Define function to generate streamed text response from string
# https://docs.streamlit.io/knowledge-base/tutorials/build-conversational-apps
def response_generator(text):
    response = random.choice(
        [
            text
        ]
    )
    for word in response.split():
        yield word + " "
        time.sleep(0.1)

# Define function to preselect search filters based on the message history
def preselect_search_filters(type=[], year=[], country=[], region=[], implementer=[], subtopic=[]):
    global st
    st.session_state.type = type
    st.session_state.year = year
    st.session_state.country = country
    st.session_state.region = region
    st.session_state.implementer = implementer
    st.session_state.subtopic = subtopic
    col1, col2, col3 = st.columns(3)
    with col1:
        st.session_state.type = st.multiselect(
            'Type(s)',
            [
                'use case', 
                'dataset', 
                'learning'
            ],
            st.session_state.type
        )                
        st.session_state.year = st.multiselect(
            'Year(s)',
            [
                '2023', 
                '2024', 
                '2025', 
                '2026', 
                '2027', 
                '2028', 
                '2029', 
                '2030'
            ],
            st.session_state.year
        )
    with col2:
        st.session_state.country = st.multiselect(
            'Country(s)',
            [
                'Ukraine',
                'Kosovo',
                'Mauritius',
                'Tunisia',
                'Western and Central Africa',
                'Chad',
                'Philippines',
                'Lebanon',
                'Afghanistan',
                'Ghana',
                'Central African Republic',
                'Turkiye',
                'Kazakhstan',
                'Morocco',
                'China',
                'Moldova',
                'Eastern and Southern Africa'
            ],
            st.session_state.country
        )
        st.session_state.region = st.multiselect(
            'Region(s)',
            [
                'Europe and Central Asia',
                'Eastern and Southern Africa',
                'Middle East and North Africa',
                'Western and Central Africa',
                'East Asia and Pacific',
                'South Asia'
            ],
            st.session_state.region
        )
    with col3:
        st.session_state.implementer = st.multiselect(
            'Implementer(s)',
            [
                'Ministry of Agrarian Policy and Food, Business Development Fund',
                'Ministry of Agriculture, Forestry and Rural Development',
                'Airports of Mauritius Co. Ltd (AML), Airport of Rodrigues Limited (ARL)',
                'Office des Céréales',
                'Ministry of Agriculture - Niger, Ministry of Agriculture, Hydro-Agricultural Developments and Mechanization  - Burkina Faso, Ministry of Rural Development - Mali, Ministry of Agriculture, Livestock and Rural Development - Togo',
                'Ministry of Agrarian Policy and Food, Partial Credit Guarantee Fund',
                'Ministry of Agriculture and Forestry - Sierra Leone, Ministry of Agricultural Development - Chad, Ministry of Food and Agriculture - Ghana',
                'Ministère de la Santé Publique',
                'Department of Agriculture',
                'Council for Development and Reconstruction',
                'Aga Khan Foundation USA, The United Nations Office for Project Services',
                'The Tree Crops Development Authority (TCDA), The Ghana Cocoa Board (COCOBOD)',
                'Ministry of Agriculture and Rural Development',
                'Directorate General of Forestry (OGM)',
                'Forestry and Wildlife Committee of the Ministry of Ecology and Natural Resources',
                "Caisse Nationale de Securité Sociale, Agence pour le Développement Agricole, Ministère de la Transition Energétique et du Développement Durable (MTEDD), Agence Nationale des Eaux et Forêts (ANEF), Ministère de l'Agriculture, de la Pêche Maritime, du Développement Rural et des Eaux et Forêts, Direction Générale de la Météorologie (DGM), Ministry of Economy and Finance, Ministère de l’Équipement et de l’Eau (MEE), Agence Nationale de Développement des Zones Oasiennes et Arganier (ANDZOA)",
                'Hunan Provincial Department of Agriculture and Rural Affairs',
                'Ministry of Agriculture and Food Industry',
                'Ministry of Agriculture, Irrigation, Natural Resources and Livestock, Ministry of Agriculture',
                'Department of Agriculture - Bureau of Fisheries and Aquatic Resources'
            ],
            st.session_state.implementer
        )
        st.session_state.subtopic = st.multiselect(
            'Subtopic(s)',
            [
                'Agricultural Extension, Research, and Other Support Activities',
                'Public Administration - Agriculture, Fishing & Forestry',
                'Irrigation and Drainage',
                'Fisheries',
                'Other Water Supply, Sanitation and Waste Management',
                'Tourism',
                'Public Administration - Transportation',
                'Aviation',
                'Other Agriculture, Fishing and Forestry',
                'Agricultural markets, commercialization and agri-business',
                'Crops',
                'Livestock',
                'Public Administration - Industry, Trade and Services',
                'Public Administration - Water, Sanitation and Waste Management',
                'Water Supply',
                'Sanitation',
                'ICT Services',
                'Forestry',
                'Other Public Administration',
                'Social Protection',
                'Health'
            ],
            st.session_state.subtopic
        )

# Define function to get more information on a record from the knowledge base using its id
def get_more_information(id):
    # Get the metadata of the record from the knowledge base
    key = list(index.fetch(ids=[id])['vectors'])[0]
    metadata = index.fetch(ids=[id])['vectors'][key]['metadata']
    # Clean up the metadata
    metadata.pop('short_description', None)
    metadata.pop('text_to_insert', None)
    documents = {}
    for doc in metadata['document(s)']:
        doc = ast.literal_eval('{' + doc + '}')
        documents.update(doc)
    metadata['document(s)'] = documents
    # Return the metadata
    return str(metadata)

# Define function to search the knowledge base using a query and selected filters
def search_knowledge_base(query, type, year, country, region, implementer, subtopic):
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
    if implementer is not []:
        filter_dict["implementer"] = {"$in": implementer}
    if subtopic is not []:
        filter_dict["subtopic"] = {"$in": subtopic}
    # Query the knowledge base index
    top_k_matches = query_pinecone_index(
        embedding, 
        top_k=5, 
        include_metadata=True, 
        include_values=False
    )
    # Extract the metadata from the top k matches
    top_k_matches_list = []
    for match in top_k_matches['matches']:
        top_k_matches_list.append(match['metadata']['text_to_insert'])
    # Return the top k matches
    return top_k_matches_list

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
#@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
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
        return call_tool(tool_calls[0], functions)

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
                        "description": """
                            Resource type(s). Options include:
                            [
                                'use case', 
                                'dataset', 
                                'learning'
                            ]
                        """
                    },
                    "year": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": """
                            The year(s) that the learning/use case/dataset covers. Options include:
                            [
                                '2023', 
                                '2024', 
                                '2025', 
                                '2026', 
                                '2027', 
                                '2028', 
                                '2029', 
                                '2030'
                            ]
                        """
                    },
                    "country": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": """
                            The country(s) involved. Options include:
                            [
                                'Ukraine',
                                'Kosovo',
                                'Mauritius',
                                'Tunisia',
                                'Western and Central Africa',
                                'Chad',
                                'Philippines',
                                'Lebanon',
                                'Afghanistan',
                                'Ghana',
                                'Central African Republic',
                                'Turkiye',
                                'Kazakhstan',
                                'Morocco',
                                'China',
                                'Moldova',
                                'Eastern and Southern Africa'
                            ]
                        """
                    },
                    "region": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": """
                            The region(s) involved. Options include:
                            [
                                'Europe and Central Asia',
                                'Eastern and Southern Africa',
                                'Middle East and North Africa',
                                'Western and Central Africa',
                                'East Asia and Pacific',
                                'South Asia'
                            ]
                        """
                    },
                    "implementer": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": """
                            The implementer(s) involved. Options include:
                            [
                                'Ministry of Agrarian Policy and Food, Business Development Fund',
                                'Ministry of Agriculture, Forestry and Rural Development',
                                'Airports of Mauritius Co. Ltd (AML), Airport of Rodrigues Limited (ARL)',
                                'Office des Céréales',
                                'Ministry of Agriculture - Niger, Ministry of Agriculture, Hydro-Agricultural Developments and Mechanization  - Burkina Faso, Ministry of Rural Development - Mali, Ministry of Agriculture, Livestock and Rural Development - Togo',
                                'Ministry of Agrarian Policy and Food, Partial Credit Guarantee Fund',
                                'Ministry of Agriculture and Forestry - Sierra Leone, Ministry of Agricultural Development - Chad, Ministry of Food and Agriculture - Ghana',
                                'Ministère de la Santé Publique',
                                'Department of Agriculture',
                                'Council for Development and Reconstruction',
                                'Aga Khan Foundation USA, The United Nations Office for Project Services',
                                'The Tree Crops Development Authority (TCDA), The Ghana Cocoa Board (COCOBOD)',
                                'Ministry of Agriculture and Rural Development',
                                'Directorate General of Forestry (OGM)',
                                'Forestry and Wildlife Committee of the Ministry of Ecology and Natural Resources',
                                "Caisse Nationale de Securité Sociale, Agence pour le Développement Agricole, Ministère de la Transition Energétique et du Développement Durable (MTEDD), Agence Nationale des Eaux et Forêts (ANEF), Ministère de l'Agriculture, de la Pêche Maritime, du Développement Rural et des Eaux et Forêts, Direction Générale de la Météorologie (DGM), Ministry of Economy and Finance, Ministère de l’Équipement et de l’Eau (MEE), Agence Nationale de Développement des Zones Oasiennes et Arganier (ANDZOA)",
                                'Hunan Provincial Department of Agriculture and Rural Affairs',
                                'Ministry of Agriculture and Food Industry',
                                'Ministry of Agriculture, Irrigation, Natural Resources and Livestock, Ministry of Agriculture',
                                'Department of Agriculture - Bureau of Fisheries and Aquatic Resources'
                            ]
                        """
                    },
                    "subtopic": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": """
                            The agricultural subtopic(s) involved. Options include:
                            [
                                'Agricultural Extension, Research, and Other Support Activities',
                                'Public Administration - Agriculture, Fishing & Forestry',
                                'Irrigation and Drainage',
                                'Fisheries',
                                'Other Water Supply, Sanitation and Waste Management',
                                'Tourism',
                                'Public Administration - Transportation',
                                'Aviation',
                                'Other Agriculture, Fishing and Forestry',
                                'Agricultural markets, commercialization and agri-business',
                                'Crops',
                                'Livestock',
                                'Public Administration - Industry, Trade and Services',
                                'Public Administration - Water, Sanitation and Waste Management',
                                'Water Supply',
                                'Sanitation',
                                'ICT Services',
                                'Forestry',
                                'Other Public Administration',
                                'Social Protection',
                                'Health'
                            ]
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
            "content": "Welcome to the AgriFood Data Lab! Explore agricultural use cases, datasets, and learning resources, with AI-enabled search, retrieval, and analysis capabilities. How can we help you today?"
        }
    )
    # Display the assistant welcome message
    with st.chat_message(name="assistant", avatar=img_bytes):
        st.write_stream(
            response_generator(
                "Welcome to the AgriFood Data Lab! Explore agricultural use cases, datasets, and learning resources, with AI-enabled search, retrieval, and analysis capabilities. How can we help you today?"
            )
        )

# Rerun the Streamlit chat if already initialized
elif "messages" in st.session_state:
    for message in st.session_state.messages:
        # Redisplay the user and assistant chat messages (without streaming effect)
        if message["role"] == "assistant":
            with st.chat_message(name="assistant", avatar=img_bytes):
                st.markdown(message["content"])
            # Redisplay the filters if the assistant message is about preselecting search filters
            if message["content"] == "Thank you. We've added some optional filters that you can edit to help us narrow down your search.":
                with st.chat_message(name="user", avatar=img_bytes_black):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.multiselect(
                            'Type(s)',
                            [
                                'use case', 
                                'dataset', 
                                'learning'
                            ],
                            st.session_state.type
                        )                
                        st.multiselect(
                            'Year(s)',
                            [
                                '2023', 
                                '2024', 
                                '2025', 
                                '2026', 
                                '2027', 
                                '2028', 
                                '2029', 
                                '2030'
                            ],
                            st.session_state.year
                        )
                    with col2:
                        st.multiselect(
                            'Country(s)',
                            [
                                'Ukraine',
                                'Kosovo',
                                'Mauritius',
                                'Tunisia',
                                'Western and Central Africa',
                                'Chad',
                                'Philippines',
                                'Lebanon',
                                'Afghanistan',
                                'Ghana',
                                'Central African Republic',
                                'Turkiye',
                                'Kazakhstan',
                                'Morocco',
                                'China',
                                'Moldova',
                                'Eastern and Southern Africa'
                            ],
                            st.session_state.country
                        )
                        st.multiselect(
                            'Region(s)',
                            [
                                'Europe and Central Asia',
                                'Eastern and Southern Africa',
                                'Middle East and North Africa',
                                'Western and Central Africa',
                                'East Asia and Pacific',
                                'South Asia'
                            ],
                            st.session_state.region
                        )
                    with col3:
                        st.multiselect(
                            'Implementer(s)',
                            [
                                'Ministry of Agrarian Policy and Food, Business Development Fund',
                                'Ministry of Agriculture, Forestry and Rural Development',
                                'Airports of Mauritius Co. Ltd (AML), Airport of Rodrigues Limited (ARL)',
                                'Office des Céréales',
                                'Ministry of Agriculture - Niger, Ministry of Agriculture, Hydro-Agricultural Developments and Mechanization  - Burkina Faso, Ministry of Rural Development - Mali, Ministry of Agriculture, Livestock and Rural Development - Togo',
                                'Ministry of Agrarian Policy and Food, Partial Credit Guarantee Fund',
                                'Ministry of Agriculture and Forestry - Sierra Leone, Ministry of Agricultural Development - Chad, Ministry of Food and Agriculture - Ghana',
                                'Ministère de la Santé Publique',
                                'Department of Agriculture',
                                'Council for Development and Reconstruction',
                                'Aga Khan Foundation USA, The United Nations Office for Project Services',
                                'The Tree Crops Development Authority (TCDA), The Ghana Cocoa Board (COCOBOD)',
                                'Ministry of Agriculture and Rural Development',
                                'Directorate General of Forestry (OGM)',
                                'Forestry and Wildlife Committee of the Ministry of Ecology and Natural Resources',
                                "Caisse Nationale de Securité Sociale, Agence pour le Développement Agricole, Ministère de la Transition Energétique et du Développement Durable (MTEDD), Agence Nationale des Eaux et Forêts (ANEF), Ministère de l'Agriculture, de la Pêche Maritime, du Développement Rural et des Eaux et Forêts, Direction Générale de la Météorologie (DGM), Ministry of Economy and Finance, Ministère de l’Équipement et de l’Eau (MEE), Agence Nationale de Développement des Zones Oasiennes et Arganier (ANDZOA)",
                                'Hunan Provincial Department of Agriculture and Rural Affairs',
                                'Ministry of Agriculture and Food Industry',
                                'Ministry of Agriculture, Irrigation, Natural Resources and Livestock, Ministry of Agriculture',
                                'Department of Agriculture - Bureau of Fisheries and Aquatic Resources'
                            ],
                            st.session_state.implementer
                        )
                        st.multiselect(
                            'Subtopic(s)',
                            [
                                'Agricultural Extension, Research, and Other Support Activities',
                                'Public Administration - Agriculture, Fishing & Forestry',
                                'Irrigation and Drainage',
                                'Fisheries',
                                'Other Water Supply, Sanitation and Waste Management',
                                'Tourism',
                                'Public Administration - Transportation',
                                'Aviation',
                                'Other Agriculture, Fishing and Forestry',
                                'Agricultural markets, commercialization and agri-business',
                                'Crops',
                                'Livestock',
                                'Public Administration - Industry, Trade and Services',
                                'Public Administration - Water, Sanitation and Waste Management',
                                'Water Supply',
                                'Sanitation',
                                'ICT Services',
                                'Forestry',
                                'Other Public Administration',
                                'Social Protection',
                                'Health'
                            ],
                            st.session_state.subtopic
                        )
        else:
            with st.chat_message(name="user", avatar=img_bytes_black):            
                st.markdown(message["content"])                    

# Add Streamlit chat user input
if prompt := st.chat_input("Type your reply here..."):
    # Add the user message to the chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display the user message
    with st.chat_message("user", avatar=img_bytes_black):
        st.markdown(prompt)

# Add Streamlit chat assistant response asking for more details
if len(st.session_state.messages) == 2 and st.session_state.messages[-2]["content"] == "Welcome to the AgriFood Data Lab! Explore agricultural use cases, datasets, and learning resources, with AI-enabled search, retrieval, and analysis capabilities. How can we help you today?":
    # Add the assistant message to the chat history
    st.session_state.messages.append(
        {
            "role": "assistant", 
            "content": "Could you describe what you're looking for to us in more detail?"
        }
    )
    # Display the assistant message (with streaming effect)
    with st.chat_message("assistant", avatar=img_bytes):
            st.write_stream(
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
                model=GPT_MODEL,
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
            matches = search_knowledge_base(
                query=st.session_state.messages[-2]["content"],
                type=[],
                year=[],
                country=[],
                region=[],
                implementer=[],
                subtopic=[]
            )
        # Display the matches (with streaming effect)    
        st.write_stream(
                response_generator(
                    "We used the conversation and selected filters to run an AI-enabled semantic search on our database. Here are the top matches:"
                )
            )
        for match in matches:
            st.write_stream(
                    response_generator(
                        match
                    )
                )
        st.write_stream(
            response_generator(
                "Would you like to know more about any of these matches or search for something else?"
            )
        )
        # Add the assistant message to the chat history
        st.session_state.messages.append(
            {
                "role": "assistant", 
                "content": """
                We used the conversation and selected filters to run an AI-enabled semantic search on our database. 
                Here are the top matches:  \n  \n""" + "  \n  \n".join(matches) + """  \n  \nWould you like to know 
                more about any of these matches or search for something else?"""
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
        model=GPT_MODEL,
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
        st.write_stream(
            response_generator(
                response
            )
        )
    
    