from src.retrieval.models import (
    RetrievalRequest,
    RetrievalResponse,
)

from src.retrieval.registry import ProviderRegistry
from src.retrieval.providers.base import RetrievalProvider
from src.retrieval.ranking.pipeline import RankingPipeline


class RetrievalPipeline:
    """
    Enterprise Retrieval Pipeline.

    Responsibilities
    ----------------
    - Own retrieval providers
    - Execute all providers
    - Merge retrieval results

    Future Responsibilities
    -----------------------
    - Ranking
    - Deduplication
    - Parallel execution
    - Metrics
    - Tracing
    - Caching
    """
    def __init__(
        self,
        ranking_pipeline: RankingPipeline,
    ):

        self._registry = ProviderRegistry()

        self._ranking_pipeline = ranking_pipeline
    # ---------------------------------------------------------
    # Provider Management
    # ---------------------------------------------------------

    def add_provider(
        self,
        provider: RetrievalProvider,
    ) -> None:
        self._registry.register(provider)

    # ---------------------------------------------------------
    # Retrieval
    # ---------------------------------------------------------



    def retrieve(
        self,
        request: RetrievalRequest,
    ) -> RetrievalResponse:
        print("\n" + "=" * 80)
        print("RETRIEVAL PIPELINE")
        print("=" * 80)
        print(f"Query : {request.query}")

        if self._registry.count() == 0:
            raise RuntimeError(
                "No retrieval providers registered."
            )

        documents = []

        for provider in self._registry.providers():

            response = provider.retrieve(request)

            documents.extend(
                response.documents
            )


        ranked_documents = self._ranking_pipeline.rank(
            documents
        )
        print(f"\nRetrieved {len(ranked_documents)} documents")
        return RetrievalResponse(
            documents=ranked_documents
        )