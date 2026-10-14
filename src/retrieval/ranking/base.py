from abc import ABC, abstractmethod

from src.retrieval.models import RetrievedDocument


class RankingStrategy(ABC):
    """
    Base interface for all ranking strategies.

    A ranking strategy receives retrieved documents
    and returns them in ranked order.
    """

    @abstractmethod
    def rank(
        self,
        documents: list[RetrievedDocument],
    ) -> list[RetrievedDocument]:
        """
        Rank retrieved documents.
        """
        pass