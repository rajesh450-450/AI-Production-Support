from src.retrieval.bootstrap import create_retrieval_pipeline
from src.retrieval.models import RetrievalRequest


def main():

    print("=" * 60)
    print("Testing End-to-End Retrieval")
    print("=" * 60)

    # ---------------------------------------------------------
    # Create Pipeline
    # ---------------------------------------------------------

    pipeline = create_retrieval_pipeline()

    # ---------------------------------------------------------
    # Build Request
    # ---------------------------------------------------------

    request = RetrievalRequest(
        query="Why did Oracle validation fail?",
        top_k=5,
    )

    # ---------------------------------------------------------
    # Execute Retrieval
    # ---------------------------------------------------------

    response = pipeline.retrieve(request)

    # ---------------------------------------------------------
    # Display Results
    # ---------------------------------------------------------

    print(f"\nRetrieved Documents : {len(response.documents)}")

    for index, document in enumerate(response.documents, start=1):

        print(f"\nDocument {index}")

        print(f"ID       : {document.id}")
        print(f"Source   : {document.source}")
        print(f"Score    : {document.score}")
        print(f"Text     : {document.text}")
        print(f"Metadata : {document.metadata}")

    print("\n" + "=" * 60)
    print("End-to-End Retrieval Test Passed")
    print("=" * 60)


if __name__ == "__main__":
    main()