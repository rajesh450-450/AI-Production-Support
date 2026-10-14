from src.retrieval.models import RetrievedDocument

from src.retrieval.ranking.base import RankingStrategy


class RankingPipeline:
    """
    Executes one or more ranking strategies sequentially.
    """

    def __init__(self):

        self._strategies: list[RankingStrategy] = []

    def add_strategy(
        self,
        strategy: RankingStrategy,
    ) -> "RankingPipeline":

        self._strategies.append(strategy)

        return self

    def rank(
        self,
        documents: list[RetrievedDocument],
    ) -> list[RetrievedDocument]:

        ranked_documents = documents

        for strategy in self._strategies:

            ranked_documents = strategy.rank(
                ranked_documents
            )

        return ranked_documents

    def strategies(self) -> list[RankingStrategy]:

        return self._strategies

    def count(self) -> int:

        return len(self._strategies)