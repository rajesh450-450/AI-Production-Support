from src.retrieval.models import (
    RetrievalRequest,
    RetrievalResponse,
    RetrievedDocument,
)
from src.retrieval.providers.base import RetrievalProvider


class DummyProvider(RetrievalProvider):

    @property
    def provider_name(self) -> str:
        return "Dummy"

    def retrieve(
        self,
        request: RetrievalRequest,
    ) -> RetrievalResponse:

        document = RetrievedDocument(
            id="DOC-001",
            text=f"Dummy result for: {request.query}",
            source=self.provider_name,
            score=1.0,
        )

        return RetrievalResponse(
            documents=[document]
        )