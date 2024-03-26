### DELETE ASSISTANTS AND FILES ###

from openai import OpenAI
from settings import OPENAI_API_KEY

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

my_assistants = client.beta.assistants.list(
    limit="100"
)

# Delete all assistants and files
for assistant in my_assistants:
    
    # # Delete all files
    try:
        my_files = client.beta.assistants.files.list(
            
        )
    except Exception as e:
        print("Error fetching files list:", e)
        my_files = []
    for file in my_files:
        print("Deleting file ID:", file.id)
        try:
            client.beta.assistants.files.delete(
                file_id=file.id,
                assistant_id=file.assistant_id
            )
            print("File deleted successfully.")
        except Exception as e:
            print("Error deleting file:", e)
    
    # Delete the assistant
    try:
        client.beta.assistants.delete(
            assistant_id=assistant.id
        )
    except Exception as e:
        print(e)