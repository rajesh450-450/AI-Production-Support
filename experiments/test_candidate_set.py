from src.indexing.chunk_store import ChunkStore
from src.indexing.faiss_index import FaissIndex
from src.retrieval.knowledge_retriever import KnowledgeRetriever
from src.retrieval.models import RetrievalRequest
from src.retrieval.query_understanding import QueryUnderstanding


def main() -> None:

    print()
    print("=" * 70)
    print("6.10.4 CANDIDATE SET CONSTRUCTION TEST")
    print("=" * 70)

    chunk_store = ChunkStore(
        db_path="data/knowledge.db"
    )

    faiss_index = FaissIndex(
        index_path="data/knowledge.faiss",
        mapping_path="data/faiss_chunk_ids.json",
    )

    query_understanding = QueryUnderstanding()

    retriever = KnowledgeRetriever(
        chunk_store=chunk_store,
        query_understanding=query_understanding,
        faiss_index=faiss_index,
    )

    try:

        # ====================================================
        # TEST 1: SEMANTIC QUERY
        # ====================================================

        print()
        print("TEST 1: Semantic query")
        print("-" * 70)

        request = RetrievalRequest(
            query="What are recent production incidents?",
            top_k=5,
        )

        response = retriever.retrieve(
            request
        )

        print(
            f"Candidates returned : "
            f"{len(response.documents)}"
        )

        if not response.documents:
            print("FAIL: No candidates returned.")
            return

        print("PASS: Semantic candidates returned.")

        for document in response.documents:
            print(
                f"  {document.id} "
                f"(score={document.score})"
            )

        # ====================================================
        # TEST 2: JIRA QUERY
        # ====================================================

        print()
        print("TEST 2: Jira query")
        print("-" * 70)

        request = RetrievalRequest(
            query="What happened with jira-KAN-1?",
            top_k=5,
        )

        response = retriever.retrieve(
            request
        )

        print(
            f"Candidates returned : "
            f"{len(response.documents)}"
        )

        if not response.documents:
            print("FAIL: No Jira candidates returned.")
            return

        jira_candidates = [
            document
            for document in response.documents
            if document.source == "jira"
        ]

        semantic_candidates = [
            document
            for document in response.documents
            if document.source != "jira"
        ]

        print(
            f"Jira candidates     : "
            f"{len(jira_candidates)}"
        )

        print(
            f"Semantic candidates : "
            f"{len(semantic_candidates)}"
        )

        if not jira_candidates:
            print(
                "FAIL: Jira exact candidates not found."
            )
            return

        print(
            "PASS: Jira exact candidates returned."
        )

        for document in jira_candidates:
            print(
                f"  {document.id}"
            )

        if semantic_candidates:
            print(
                "PASS: Semantic candidates also returned."
            )

        # ====================================================
        # TEST 3: DUPLICATE CHECK
        # ====================================================

        print()
        print("TEST 3: Duplicate candidate check")
        print("-" * 70)

        ids = [
            document.id
            for document in response.documents
        ]

        unique_ids = set(ids)

        print(
            f"Total candidates : {len(ids)}"
        )

        print(
            f"Unique chunk IDs  : {len(unique_ids)}"
        )

        if len(ids) != len(unique_ids):
            print(
                "FAIL: Duplicate chunk IDs found."
            )
            return

        print(
            "PASS: No duplicate chunk IDs."
        )

        # ====================================================
        # FINAL RESULT
        # ====================================================

        print()
        print("=" * 70)
        print(
            "PASS: 6.10.4 CANDIDATE SET TEST COMPLETED"
        )
        print("=" * 70)

    finally:

        chunk_store.close()


if __name__ == "__main__":
    main()