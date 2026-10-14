from src.memory.sqlite_memory import sqlite_memory

from src.retrieval.models import (
    RetrievalRequest,
    RetrievalResponse,
    RetrievedDocument,
)

from src.retrieval.providers.base import RetrievalProvider


class SQLiteProvider(RetrievalProvider):
    """
    Retrieval provider for durable knowledge
    stored in SQLite.
    """
    def __init__(self, sqlite_memory):
        self.sqlite_memory = sqlite_memory

    @property
    def provider_name(self) -> str:
        return "sqlite"

    def retrieve(
        self,
        request: RetrievalRequest,
    ) -> RetrievalResponse:

        documents = self.sqlite_memory.search(
            query=request.query,
            top_k=request.top_k,
        )

        results = []

        for document in documents:

            results.append(
                RetrievedDocument(
                    id=document.id,
                    text=document.text,
                    metadata=document.metadata,
                    source=self.provider_name,
                    score=1.0,
                )
            )

        return RetrievalResponse(
            documents=results
        )