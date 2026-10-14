from src.retrieval.models import RetrievalRequest
from src.retrieval.pipeline import RetrievalPipeline
from src.retrieval.providers.dummy_provider import DummyProvider


def main():

    print("=" * 60)
    print("Testing Retrieval Pipeline")
    print("=" * 60)

    # -----------------------------------------------------
    # Create Pipeline
    # -----------------------------------------------------

    pipeline = RetrievalPipeline()

    # -----------------------------------------------------
    # Register Providers
    # -----------------------------------------------------

    pipeline.add_provider(
        DummyProvider()
    )

    # -----------------------------------------------------
    # Create Request
    # -----------------------------------------------------

    request = RetrievalRequest(
        query="Why did Oracle validation fail?",
        top_k=3,
    )

    # -----------------------------------------------------
    # Execute Retrieval
    # -----------------------------------------------------

    response = pipeline.retrieve(request)

    # -----------------------------------------------------
    # Print Results
    # -----------------------------------------------------

    print(f"\nDocuments Retrieved : {len(response.documents)}")

    for i, document in enumerate(response.documents, start=1):

        print(f"\nDocument {i}")

        print(f"  ID       : {document.id}")
        print(f"  Source   : {document.source}")
        print(f"  Score    : {document.score}")
        print(f"  Text     : {document.text}")
        print(f"  Metadata : {document.metadata}")

    print("\n" + "=" * 60)
    print("Retrieval Pipeline Test Passed")
    print("=" * 60)


if __name__ == "__main__":
    main()