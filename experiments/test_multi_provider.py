from src.memory.semantic_memory import semantic_memory
from src.memory.sqlite_memory import sqlite_memory
from src.memory.conversation_memory import conversation_memory

from src.retrieval.bootstrap import create_retrieval_pipeline
from src.retrieval.models import RetrievalRequest


def print_results(response):

    print("\n")
    print("=" * 70)
    print("Multi-Provider Retrieval Results")
    print("=" * 70)

    for index, document in enumerate(
        response.documents,
        start=1,
    ):

        print(f"\nDocument #{index}")
        print(f"Provider : {document.source}")
        print(f"Score    : {document.score}")
        print(f"Content  : {document.text}")
        print(f"Metadata : {document.metadata}")

    print("\n")
    print("=" * 70)
    print(
        f"Total Documents Retrieved : {len(response.documents)}"
    )
    print("=" * 70)


def main():

    # ---------------------------------------------------------
    # Clear Memories
    # ---------------------------------------------------------

    semantic_memory.clear()

    sqlite_memory.clear()

    conversation_memory.clear()

    # ---------------------------------------------------------
    # Populate FAISS
    # ---------------------------------------------------------

    semantic_memory.add(
        text="Spark executor memory tuning improves performance.",
        metadata={
            "category": "Spark",
        },
    )

    semantic_memory.add(
        text="Databricks cluster restart clears stale executors.",
        metadata={
            "category": "Databricks",
        },
    )

    # ---------------------------------------------------------
    # Populate SQLite
    # ---------------------------------------------------------

    sqlite_memory.add(
        text="Restarting the NiFi processor resolves this issue.",
        metadata={
            "category": "NiFi",
        },
    )

    # ---------------------------------------------------------
    # Populate Conversation Memory
    # ---------------------------------------------------------


    conversation_memory.add(
        role="user",
        text="Yesterday we investigated a Spark executor failure",
    )

    conversation_memory.add(
        role="assistant",
        text="The issue was caused by insufficient executor memory.",
    )


    # ---------------------------------------------------------
    # Create Retrieval Pipeline
    # ---------------------------------------------------------

    pipeline = create_retrieval_pipeline()

    # ---------------------------------------------------------
    # Retrieve
    # ---------------------------------------------------------

    response = pipeline.retrieve(

        RetrievalRequest(
            query="Databricks restart Oracle Spark executor",
            top_k=5,
        )

    )

    # ---------------------------------------------------------
    # Assertions
    # ---------------------------------------------------------


    scores = [
        document.score
        for document in response.documents
    ]

    assert scores == sorted(
        scores,
        reverse=True,
    )

    providers = {
        document.source.lower()
        for document in response.documents
    }


    print(response)
    print_results(
        response
    )

    print("\nMulti-Provider Integration Test Passed.\n")


if __name__ == "__main__":

    main()