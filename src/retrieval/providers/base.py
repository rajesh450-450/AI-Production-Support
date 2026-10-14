from abc import ABC, abstractmethod

from src.retrieval.models import (
    RetrievalRequest,
    RetrievalResponse,
)


class RetrievalProvider(ABC):
    """
    Base class for all retrieval providers.

    A retrieval provider is responsible for retrieving
    knowledge from exactly one source.

    Examples:
        - FAISS
        - SQLite
        - Conversation Memory
        - REST API
        - MCP Server
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """
        Human-readable provider name.
        """
        pass

    @abstractmethod
    def retrieve(
        self,
        request: RetrievalRequest,
    ) -> RetrievalResponse:
        """
        Retrieve relevant documents.

        Args:
            request:
                Retrieval request.

        Returns:
            RetrievalResponse
        """
        pass