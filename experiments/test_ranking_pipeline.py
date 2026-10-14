from src.retrieval.models import RetrievedDocument
from src.retrieval.ranking.pipeline import RankingPipeline
from src.retrieval.ranking.score_strategy import (
    ScoreRankingStrategy,
)


def print_results(documents: list[RetrievedDocument]):

    print("\n")
    print("=" * 70)
    print("Ranking Pipeline Results")
    print("=" * 70)

    for index, document in enumerate(documents, start=1):

        print(f"\nDocument #{index}")
        print(f"Score    : {document.score}")
        print(f"Provider : {document.source}")
        print(f"Content  : {document.text}")

    print("\n")
    print("=" * 70)
    print(f"Total Documents : {len(documents)}")
    print("=" * 70)


def main():

    documents = [

        RetrievedDocument(
            id="1",
            text="Low score document",
            metadata={
                "category": "Test",
            },
            source="FAISS",
            score=0.32,
        ),

        RetrievedDocument(
            id="2",
            text="Highest score document",
            metadata={
                "category": "Test",
            },
            source="SQLite",
            score=0.98,
        ),

        RetrievedDocument(
            id="3",
            text="Medium score document",
            metadata={
                "category": "Test",
            },
            source="Conversation",
            score=0.71,
        ),

    ]

    ranking_pipeline = (
        RankingPipeline()
        .add_strategy(
            ScoreRankingStrategy()
        )
    )

    ranked_documents = ranking_pipeline.rank(
        documents
    )

    # ---------------------------------------------------------
    # Assertions
    # ---------------------------------------------------------

    assert len(ranked_documents) == 3

    previous_score = float("inf")

    for document in ranked_documents:

        assert document.score <= previous_score

        previous_score = document.score

    assert ranked_documents[0].id == "2"
    assert ranked_documents[1].id == "3"
    assert ranked_documents[2].id == "1"

    print_results(
        ranked_documents
    )

    print("\nRanking Pipeline Test Passed.\n")


if __name__ == "__main__":

    main()