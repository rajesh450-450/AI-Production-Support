from src.indexing.chunk_store import ChunkStore
from src.indexing.faiss_index import FaissIndex

from src.retrieval.knowledge_retriever import KnowledgeRetriever
from src.retrieval.models import (
    RetrievalRequest,
    RetrievedDocument,
)
from src.retrieval.query_understanding import (
    QueryUnderstanding,
)


def print_results(
    documents: list[RetrievedDocument],
) -> None:

    for index, document in enumerate(
        documents,
        start=1,
    ):
        print()
        print(
            f"Result {index}"
        )
        print(
            f"chunk_id       : {document.id}"
        )
        print(
            f"source         : {document.source}"
        )
        print(
            f"retrieval_type : "
            f"{document.metadata.get('retrieval_type')}"
        )
        print(
            f"score          : {document.score}"
        )
        print(
            f"text           : "
            f"{document.text[:150]}"
        )


def main() -> None:

    print()
    print("=" * 70)
    print("6.10.6 KNOWLEDGE RETRIEVAL END-TO-END TEST")
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
        # TEST 1: NORMAL SEMANTIC QUERY
        # ====================================================

        print()
        print("TEST 1: Semantic retrieval")
        print("-" * 70)

        request = RetrievalRequest(
            query=(
                "What are the recent production "
                "incidents and their root causes?"
            ),
            top_k=5,
        )

        response = retriever.retrieve(
            request
        )

        print(
            f"Retrieved documents : "
            f"{len(response.documents)}"
        )

        if not response.documents:
            print(
                "FAIL: Semantic retrieval returned no results."
            )
            return

        print(
            "PASS: Semantic retrieval returned documents."
        )

        if len(response.documents) > request.top_k:
            print(
                "FAIL: top_k constraint violated."
            )
            return

        print(
            "PASS: top_k constraint respected."
        )

        print_results(
            response.documents
        )

        # ----------------------------------------------------
        # Verify SQLite authority
        # ----------------------------------------------------

        for document in response.documents:

            chunk = chunk_store.get_by_id(
                document.id
            )

            if chunk is None:
                print(
                    f"FAIL: {document.id} "
                    "does not exist in SQLite."
                )
                return

            if document.text != chunk.text:
                print(
                    f"FAIL: Retrieved text for "
                    f"{document.id} does not match SQLite."
                )
                return

        print(
            "PASS: All semantic results match "
            "authoritative SQLite chunks."
        )

        # ====================================================
        # TEST 2: JIRA QUERY
        # ====================================================

        print()
        print("TEST 2: Jira exact + semantic retrieval")
        print("-" * 70)

        request = RetrievalRequest(
            query="What happened with jira-KAN-1?",
            top_k=5,
        )

        response = retriever.retrieve(
            request
        )

        print(
            f"Retrieved documents : "
            f"{len(response.documents)}"
        )

        if not response.documents:
            print(
                "FAIL: Jira retrieval returned no results."
            )
            return

        print(
            "PASS: Jira retrieval returned candidates."
        )

        print_results(
            response.documents
        )

        # ----------------------------------------------------
        # Verify exact Jira candidates
        # ----------------------------------------------------

        exact_results = [
            document
            for document in response.documents
            if document.metadata.get(
                "retrieval_type"
            ) == "exact"
        ]

        if not exact_results:
            print(
                "FAIL: No exact Jira candidates found."
            )
            return

        print(
            f"PASS: Exact Jira candidates found "
            f"({len(exact_results)})."
        )

        # ----------------------------------------------------
        # Verify exact candidates come first
        # ----------------------------------------------------

        first_semantic_index = None

        for index, document in enumerate(
            response.documents
        ):
            if document.metadata.get(
                "retrieval_type"
            ) == "semantic":

                first_semantic_index = index
                break

        if first_semantic_index is not None:

            for document in response.documents[
                first_semantic_index:
            ]:

                if document.metadata.get(
                    "retrieval_type"
                ) == "exact":

                    print(
                        "FAIL: Exact Jira result "
                        "appears after semantic result."
                    )
                    return

        print(
            "PASS: Exact Jira candidates "
            "are ranked before semantic candidates."
        )

        # ====================================================
        # TEST 3: DUPLICATE CHECK
        # ====================================================

        print()
        print("TEST 3: Duplicate chunk check")
        print("-" * 70)

        ids = [
            document.id
            for document in response.documents
        ]

        unique_ids = set(ids)

        print(
            f"Total results : {len(ids)}"
        )

        print(
            f"Unique IDs    : {len(unique_ids)}"
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
        # TEST 4: RetrievedDocument CONTRACT
        # ====================================================

        print()
        print("TEST 4: RetrievedDocument contract")
        print("-" * 70)

        for document in response.documents:

            if not document.id:
                print(
                    "FAIL: RetrievedDocument has no id."
                )
                return

            if not document.text:
                print(
                    f"FAIL: {document.id} "
                    "has no text."
                )
                return

            if not document.source:
                print(
                    f"FAIL: {document.id} "
                    "has no source."
                )
                return

            if document.score is None:
                print(
                    f"FAIL: {document.id} "
                    "has no score."
                )
                return

            if not isinstance(
                document.metadata,
                dict,
            ):
                print(
                    f"FAIL: {document.id} "
                    "metadata is not a dictionary."
                )
                return

        print(
            "PASS: All results satisfy "
            "RetrievedDocument contract."
        )

        # ====================================================
        # FINAL RESULT
        # ====================================================

        print()
        print("=" * 70)
        print(
            "PASS: 6.10.6 END-TO-END TEST COMPLETED"
        )
        print("=" * 70)

    finally:

        chunk_store.close()


if __name__ == "__main__":
    main()