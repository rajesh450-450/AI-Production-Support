# test_embed.py

import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# import logging

# logging.basicConfig(level=logging.DEBUG)
# logging.getLogger("httpx").setLevel(logging.DEBUG)
# logging.getLogger("httpcore").setLevel(logging.DEBUG)

print("Client created")

print("Calling embedding API...")

response = client.models.embed_content(
    model="gemini-embedding-001",
    contents="Hello World"
)

print("Success")
print(len(response.embeddings[0].values))