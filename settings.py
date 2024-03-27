import streamlit as st

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

LLM_MODEL = "gpt-3.5-turbo-1106"

EMBEDDING_MODEL = "text-embedding-3-small"

PINECONE_API_KEY = st.secrets["PINECONE_API_KEY"]
PINECONE_INDEX = "agrifooddatalab-index"
PINECONE_ENVIRONMENT = st.secrets["PINECONE_ENVIRONMENT"]

YOUTUBE_API_KEY = st.secrets["YOUTUBE_API_KEY"]

COHERE_API_KEY = st.secrets["COHERE_API_KEY"]

REGIONS = [
    'Europe and Central Asia',
    'Eastern and Southern Africa',
    'Middle East and North Africa',
    'Western and Central Africa',
    'East Asia and Pacific',
    'South Asia',
]

COUNTRIES = [
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
    'Eastern and Southern Africa',
]

YEARS = [
    '2023', 
    '2024', 
    '2025', 
    '2026', 
    '2027', 
    '2028', 
    '2029', 
    '2030',
]

TYPES = [
    'use case', 
    'dataset', 
    'learning',
]

ORGANIZATIONS = [
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

TOPICS = [
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
    'Health',
]