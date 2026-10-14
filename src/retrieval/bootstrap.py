from src.memory.semantic_memory import semantic_memory
from src.memory.sqlite_memory import sqlite_memory
from src.memory.conversation_memory import conversation_memory

from src.retrieval.pipeline import RetrievalPipeline

from src.retrieval.providers.faiss_provider import FaissProvider
from src.retrieval.providers.sqlite_provider import SQLiteProvider
from src.retrieval.providers.conversation_provider import ConversationProvider

from src.retrieval.ranking.pipeline import RankingPipeline
from src.retrieval.ranking.score_strategy import (
    ScoreRankingStrategy,
)

def create_retrieval_pipeline() -> RetrievalPipeline:
    """
    Creates a production-ready Retrieval Pipeline.

    All retrieval providers are registered here.
    """

    ranking_pipeline = (
        RankingPipeline()
            .add_strategy(
                ScoreRankingStrategy()
            )
    )

    pipeline = RetrievalPipeline(
        ranking_pipeline=ranking_pipeline,
    )

    # ---------------------------------------------------------
    # Register Providers
    # ---------------------------------------------------------

    pipeline.add_provider(
        FaissProvider(semantic_memory)
    )

    pipeline.add_provider(
        SQLiteProvider(sqlite_memory)
    )

    pipeline.add_provider(
        ConversationProvider(conversation_memory)
    )

    return pipeline