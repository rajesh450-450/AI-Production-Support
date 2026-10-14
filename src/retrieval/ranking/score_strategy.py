from src.retrieval.models import RetrievedDocument

from src.retrieval.ranking.base import RankingStrategy


class ScoreRankingStrategy(RankingStrategy):
    """
    Default ranking strategy.

    Ranks documents by score in descending order.
    """

    def rank(
        self,
        documents: list[RetrievedDocument],
    ) -> list[RetrievedDocument]:

        return sorted(
            documents,
            key=lambda document: document.score,
            reverse=True,
        )