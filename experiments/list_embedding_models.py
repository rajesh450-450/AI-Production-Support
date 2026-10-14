from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GOOGLE_API_KEY")
)

print("Embedding-capable models:\n")

for model in client.models.list():

    methods = getattr(model, "supported_actions", None)

    if methods and "embedContent" in methods:
        print(model.name)