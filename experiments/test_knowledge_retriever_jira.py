from src.indexing.chunk_store import ChunkStore
from src.retrieval.knowledge_retriever import KnowledgeRetriever
from src.retrieval.models import RetrievalRequest
from src.retrieval.query_understanding import QueryUnderstanding


def main() -> None:

    print("=" * 70)
    print("6.10.2 SQLITE EXACT JIRA LOOKUP TEST")
    print("=" * 70)
    print()

    chunk_store = ChunkStore(
        db_path="data/knowledge.db"
    )

    query_understanding = QueryUnderstanding()

    retriever = KnowledgeRetriever(
        chunk_store=chunk_store,
        query_understanding=query_understanding,
    )

    try:

        # --------------------------------------------------------
        # Test 1 - Jira exact lookup
        # --------------------------------------------------------

        query = "What is the root cause of jira-KAN-1?"

        print(f"Query: {query}")
        print()

        request = RetrievalRequest(
            query=query,
            top_k=5,
        )

        response = retriever.retrieve(request)

        documents = response.documents

        if not documents:
            print("FAIL: No documents returned.")
            return

        print(
            f"PASS: Retrieved {len(documents)} document(s)."
        )

        for document in documents:

            print()
            print(f"ID     : {document.id}")
            print(f"Source : {document.source}")
            print(f"Score  : {document.score}")
            print(f"Text   : {document.text[:150]}")

        # --------------------------------------------------------
        # Validate Jira document
        # --------------------------------------------------------

        jira_documents = [
            document
            for document in documents
            if document.id.startswith("jira-KAN-1")
        ]

        if not jira_documents:
            print()
            print(
                "FAIL: Expected Jira document "
                "jira-KAN-1 was not returned."
            )
            return

        print()
        print(
            "PASS: Correct Jira document retrieved."
        )

        # --------------------------------------------------------
        # Validate source
        # --------------------------------------------------------

        for document in jira_documents:

            if document.source != "sqlite":
                print(
                    "FAIL: Retrieved document source "
                    f"is '{document.source}', expected 'sqlite'."
                )
                return

        print(
            "PASS: Retrieved document came from SQLite."
        )

        # --------------------------------------------------------
        # Validate exact Jira document ID
        # --------------------------------------------------------

        for document in jira_documents:

            if document.id != "jira-KAN-1":
                print(
                    "FAIL: Unexpected document ID: "
                    f"{document.id}"
                )
                return

        print(
            "PASS: Exact Jira document ID matched."
        )

        # --------------------------------------------------------
        # Test 2 - Another Jira issue
        # --------------------------------------------------------

        print()
        print("-" * 70)

        query = (
            "Please investigate jira-KAN-5 "
            "and tell me what happened."
        )

        print(f"Query: {query}")
        print()

        request = RetrievalRequest(
            query=query,
            top_k=5,
        )

        response = retriever.retrieve(request)

        documents = response.documents

        if not documents:
            print(
                "FAIL: No documents returned for jira-KAN-5."
            )
            return

        print(
            f"PASS: Retrieved {len(documents)} document(s)."
        )

        jira_documents = [
            document
            for document in documents
            if document.id.startswith("jira-KAN-5")
        ]

        if not jira_documents:
            print(
                "FAIL: Expected Jira document "
                "jira-KAN-5 was not returned."
            )
            return

        print(
            "PASS: Correct Jira document retrieved."
        )

        # --------------------------------------------------------
        # Test 3 - Query without Jira ID
        # --------------------------------------------------------

        print()
        print("-" * 70)

        query = "Why are payment failures increasing?"

        print(f"Query: {query}")
        print()

        request = RetrievalRequest(
            query=query,
            top_k=5,
        )

        response = retriever.retrieve(request)

        if response.documents:
            print(
                "FAIL: Non-Jira query returned documents."
            )
            return

        print(
            "PASS: Non-Jira query did not perform "
            "Jira exact lookup."
        )

        # --------------------------------------------------------
        # Final result
        # --------------------------------------------------------

        print()
        print("=" * 70)
        print(
            "PASS: 6.10.2 SQLITE EXACT JIRA LOOKUP TEST COMPLETED"
        )
        print("=" * 70)

    finally:

        chunk_store.close()


if __name__ == "__main__":
    main()