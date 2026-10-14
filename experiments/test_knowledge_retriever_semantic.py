from src.indexing.chunk_store import ChunkStore
from src.indexing.faiss_index import FaissIndex
from src.retrieval.knowledge_retriever import KnowledgeRetriever
from src.retrieval.models import RetrievalRequest
from src.retrieval.query_understanding import QueryUnderstanding


def main() -> None:

    print()
    print("=" * 70)
    print("6.10.3 SEMANTIC QUERY -> FAISS -> SQLITE TEST")
    print("=" * 70)
    print()

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

        query = (
            "What are the recent production incidents "
            "and their root causes?"
        )

        print(f"Query : {query}")
        print()

        request = RetrievalRequest(
            query=query,
            top_k=5,
        )

        response = retriever.retrieve(
            request
        )

        print(
            f"Retrieved documents : "
            f"{len(response.documents)}"
        )
        print()

        if not response.documents:
            print("FAIL: No semantic documents retrieved.")
            return

        print(
            "PASS: Semantic retrieval returned documents."
        )

        for index, document in enumerate(
            response.documents,
            start=1,
        ):

            print()
            print(
                f"Result {index}"
            )

            print(
                f"  chunk_id : {document.id}"
            )

            print(
                f"  source   : {document.source}"
            )

            print(
                f"  score    : {document.score}"
            )

            print(
                f"  text     : "
                f"{document.text[:150]}"
            )

            sqlite_chunk = chunk_store.get_by_id(
                document.id
            )

            if sqlite_chunk is None:
                print(
                    "  FAIL: Chunk does not exist in SQLite."
                )
                return

            if sqlite_chunk.text != document.text:
                print(
                    "  FAIL: Returned text does not "
                    "match SQLite."
                )
                return

            if sqlite_chunk.metadata != document.metadata:
                print(
                    "  FAIL: Returned metadata does not "
                    "match SQLite."
                )
                return

            print(
                "  PASS: Result matches authoritative SQLite chunk."
            )

        print()
        print(
            "PASS: All FAISS results resolved successfully "
            "through SQLite."
        )

        if len(response.documents) > request.top_k:
            print(
                "FAIL: Returned more documents than top_k."
            )
            return

        print(
            "PASS: top_k constraint respected."
        )

        print()
        print("=" * 70)
        print(
            "PASS: 6.10.3 SEMANTIC RETRIEVAL TEST COMPLETED"
        )
        print("=" * 70)

    finally:

        chunk_store.close()


if __name__ == "__main__":
    main()