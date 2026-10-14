from google import genai
from src.config.settings import settings

class EmbeddingModel:
    """
    Wrapper around Google's GenAI embedding model.
    """

    def __init__(self):

        self.client = genai.Client(
            api_key=settings.google_api_key
        )

    def embed(self, text: str):

        response = self.client.models.embed_content(
            model=settings.embedding_model,
            contents=text,
        )

        return response.embeddings[0].values


embedding_model = EmbeddingModel()