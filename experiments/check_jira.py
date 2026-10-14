from src.indexing.chunk_store import ChunkStore


chunk_store = ChunkStore(
    db_path="data/knowledge.db"
)

try:
    document_id = "jira-KAN-1"

    chunks = chunk_store.get_by_document_id(
        document_id
    )

    print()
    print("Document ID:", document_id)
    print("Chunks found:", len(chunks))

    for chunk in chunks:
        print()
        print("chunk_id:", chunk.chunk_id)
        print("source:", chunk.source)
        print("title:", chunk.title)

finally:
    chunk_store.close()