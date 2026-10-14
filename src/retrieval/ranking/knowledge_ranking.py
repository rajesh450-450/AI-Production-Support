from src.retrieval.models import RetrievedDocument
from src.retrieval.ranking.base import RankingStrategy


class KnowledgeRankingStrategy(RankingStrategy):
    """
    Ranking strategy for the knowledge retrieval pipeline.

    Ranking rules:
        1. Exact candidates have highest priority.
        2. Semantic candidates are ordered by FAISS L2 distance.
           Lower distance means a better semantic match.
    """

    def rank(
        self,
        documents: list[RetrievedDocument],
    ) -> list[RetrievedDocument]:

        return sorted(
            documents,
            key=self._ranking_key,
        )

    @staticmethod
    def _ranking_key(
        document: RetrievedDocument,
    ) -> tuple[int, float]:

        retrieval_type = document.metadata.get(
            "retrieval_type"
        )

        if retrieval_type == "exact":
            return (0, 0.0)

        return (
            1,
            document.score,
        )