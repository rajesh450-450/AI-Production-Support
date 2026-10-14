from src.context.builder import ContextBuilder

from src.retrieval.models import (
    RetrievedDocument,
    RetrievalResponse,
)


def main():

    # ---------------------------------------------------------
    # Create Retrieval Response
    # ---------------------------------------------------------

    response = RetrievalResponse(

        documents=[

            RetrievedDocument(
                id="1",
                text="Yesterday we investigated a Spark executor failure.",
                source="conversation",
                score=1.0,
                metadata={
                    "role": "user",
                },
            ),

            RetrievedDocument(
                id="2",
                text="The issue was caused by insufficient executor memory.",
                source="conversation",
                score=1.0,
                metadata={
                    "role": "assistant",
                },
            ),

            RetrievedDocument(
                id="3",
                text="Spark executor memory tuning improves performance.",
                source="FAISS",
                score=0.82,
                metadata={
                    "category": "Spark",
                },
            ),

            RetrievedDocument(
                id="4",
                text="Restart Databricks cluster after configuration changes.",
                source="sqlite",
                score=0.78,
                metadata={
                    "document": "Runbook",
                },
            ),

        ]

    )

    # ---------------------------------------------------------
    # Build Context
    # ---------------------------------------------------------

    builder = ContextBuilder()

    bundle = builder.build(response)

    # ---------------------------------------------------------
    # Print Results
    # ---------------------------------------------------------

    print()
    print("=" * 70)
    print("Context Builder Test")
    print("=" * 70)

    print("\nDocuments")

    for index, document in enumerate(
        bundle.documents,
        start=1,
    ):

        print(f"\nDocument #{index}")
        print(f"Source : {document.source}")
        print(f"Text   : {document.text}")
        print(f"Metadata : {document.metadata}")

    print("\n")
    print("=" * 70)
    print("Prompt Context")
    print("=" * 70)

    print(bundle.prompt_context)

    # ---------------------------------------------------------
    # Assertions
    # ---------------------------------------------------------

    assert len(bundle.documents) == 4

    assert "Conversation" in bundle.prompt_context

    assert "Knowledge" in bundle.prompt_context

    assert "Spark executor memory tuning" in bundle.prompt_context

    assert "Yesterday we investigated" in bundle.prompt_context

    print("\n")
    print("=" * 70)
    print("Context Builder Test Passed")
    print("=" * 70)


if __name__ == "__main__":

    main()