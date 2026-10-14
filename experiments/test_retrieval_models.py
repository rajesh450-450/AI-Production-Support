from src.retrieval.models import (
    RetrievedDocument,
    RetrievalRequest,
    RetrievalResponse,
)


def main():

    print("=" * 60)
    print("Testing Retrieval Models")
    print("=" * 60)

    # -------------------------------------------------------
    # Retrieval Request
    # -------------------------------------------------------

    request = RetrievalRequest(
        query="Why did Oracle validation fail?",
        top_k=3,
        metadata={
            "environment": "DEV",
            "application": "Customer ETL",
        },
    )

    print("\nRetrievalRequest")
    print("----------------")
    print(request)

    # -------------------------------------------------------
    # Retrieved Documents
    # -------------------------------------------------------

    doc1 = RetrievedDocument(
        id="DOC-001",
        text="Oracle validation failed because CUSTOMER_ID contained NULL values.",
        source="FAISS",
        score=0.97,
        metadata={
            "table": "CUSTOMERS",
            "created_by": "AI Support",
        },
    )

    doc2 = RetrievedDocument(
        id="DOC-002",
        text="Previous incident resolved by rebuilding Oracle statistics.",
        source="SQLite",
        score=0.91,
        metadata={
            "incident": "INC-2025-1056",
        },
    )

    print("\nRetrievedDocument #1")
    print("--------------------")
    print(doc1)

    print("\nRetrievedDocument #2")
    print("--------------------")
    print(doc2)

    # -------------------------------------------------------
    # Retrieval Response
    # -------------------------------------------------------

    response = RetrievalResponse(
        documents=[
            doc1,
            doc2,
        ]
    )

    print("\nRetrievalResponse")
    print("-----------------")

    print(f"Documents Retrieved : {len(response.documents)}")

    for i, document in enumerate(response.documents, start=1):
        print(f"\nDocument {i}")
        print(f"  ID       : {document.id}")
        print(f"  Source   : {document.source}")
        print(f"  Score    : {document.score}")
        print(f"  Text     : {document.text}")
        print(f"  Metadata : {document.metadata}")

    print("\n" + "=" * 60)
    print("Retrieval Models Test Passed")
    print("=" * 60)


if __name__ == "__main__":
    main()