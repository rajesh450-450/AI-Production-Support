from src.memory.semantic_memory import SemanticMemory

from src.retrieval.models import (
    RetrievalRequest,
    RetrievalResponse,
    RetrievedDocument,
)

from src.retrieval.providers.base import RetrievalProvider


class FaissProvider(RetrievalProvider):

    def __init__(self, semantic_memory: SemanticMemory):
        self.semantic_memory = semantic_memory

    @property
    def provider_name(self) -> str:
        return "FAISS"

    def retrieve(
        self,
        request: RetrievalRequest,
    ) -> RetrievalResponse:

        results = self.semantic_memory.search(
            query=request.query,
            top_k=request.top_k,
        )

        documents = []

        for item in results:

            documents.append(
                RetrievedDocument(
                    id=item["id"],
                    text=item["text"],
                    source=self.provider_name,
                    score=item["score"],
                    metadata=item["metadata"],
                )
            )

        return RetrievalResponse(
            documents=documents
        )