import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai

# Force load .env from project root if needed
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("GOOGLE_API_KEY")

# Raise an immediate error if key is missing instead of hanging on ADC lookup
if not api_key:
    raise ValueError("GOOGLE_API_KEY is missing. Check your .env file location.")


class EmbeddingModel:
    """Wrapper around Google's GenAI embedding model."""

    def __init__(self):
        self.client = genai.Client(api_key=api_key)

    def embed(self, text: str):
        response = self.client.models.embed_content(
            model="text-embedding-004",  # Correct model identifier
            contents=text,
        )
        return response.embeddings[0].values


print("Calling embedding API...")
embedding_model = EmbeddingModel()
print(embedding_model.embed("Hello"))