from pathlib import Path
from tempfile import TemporaryDirectory

from src.indexing.chunk_store import ChunkStore
from src.indexing.models import DocumentChunk


def main() -> None:

    print()
    print("=" * 70)
    print("6.7 CHUNK METADATA & INDEXING CONTRACT TEST")
    print("=" * 70)

    with TemporaryDirectory() as temp_dir:

        db_path = Path(temp_dir) / "test_chunks.db"

        store = ChunkStore(
            db_path=str(db_path)
        )

        # --------------------------------------------------------
        # Create test chunk
        # --------------------------------------------------------

        original = DocumentChunk(
            chunk_id="confluence-98312-chunk-0003",
            document_id="confluence-98312",
            source="confluence",
            external_id="98312",
            title="Production Support FAQ",
            text=(
                "Check processor throughput.\n"
                "Check Back Pressure settings.\n"
                "Check downstream performance."
            ),
            chunk_index=3,
            metadata={
                "content_type": "knowledge_article",
                "space": "PROD",
                "priority": "high",
            },
        )

        # --------------------------------------------------------
        # Add
        # --------------------------------------------------------

        print()
        print("Adding chunk...")

        store.add(original)

        assert store.size() == 1

        print("PASS: Chunk persisted.")

        # --------------------------------------------------------
        # Get by chunk ID
        # --------------------------------------------------------

        print()
        print("Retrieving chunk by chunk_id...")

        retrieved = store.get_by_id(
            original.chunk_id
        )

        assert retrieved is not None

        print("PASS: Chunk retrieved.")

        # --------------------------------------------------------
        # Verify complete identity
        # --------------------------------------------------------

        assert retrieved.chunk_id == original.chunk_id
        assert retrieved.document_id == original.document_id
        assert retrieved.source == original.source
        assert retrieved.external_id == original.external_id
        assert retrieved.title == original.title
        assert retrieved.text == original.text
        assert retrieved.chunk_index == original.chunk_index
        assert retrieved.metadata == original.metadata

        print(
            "PASS: All DocumentChunk fields "
            "survived SQLite round-trip."
        )

        # --------------------------------------------------------
        # Parent document lookup
        # --------------------------------------------------------

        print()
        print("Retrieving by document_id...")

        chunks = store.get_by_document_id(
            original.document_id
        )

        assert len(chunks) == 1
        assert chunks[0].chunk_id == original.chunk_id

        print(
            "PASS: Parent document lookup works."
        )

        # --------------------------------------------------------
        # Upsert
        # --------------------------------------------------------

        print()
        print("Testing upsert...")

        updated = DocumentChunk(
            chunk_id=original.chunk_id,
            document_id=original.document_id,
            source=original.source,
            external_id=original.external_id,
            title=original.title,
            text="Updated chunk content.",
            chunk_index=original.chunk_index,
            metadata={
                "content_type": "knowledge_article",
                "space": "PROD",
                "priority": "critical",
            },
        )

        store.upsert(updated)

        assert store.size() == 1

        retrieved_updated = store.get_by_id(
            original.chunk_id
        )

        assert retrieved_updated is not None
        assert retrieved_updated.text == (
            "Updated chunk content."
        )
        assert (
            retrieved_updated.metadata["priority"]
            == "critical"
        )

        print(
            "PASS: Upsert updates existing chunk."
        )

        # --------------------------------------------------------
        # Delete by document
        # --------------------------------------------------------

        print()
        print("Testing delete_by_document_id...")

        deleted = store.delete_by_document_id(
            original.document_id
        )

        assert deleted == 1
        assert store.size() == 0

        assert (
            store.get_by_id(original.chunk_id)
            is None
        )

        print(
            "PASS: Document chunks can be deleted."
        )

        store.close()

    print()
    print("=" * 70)
    print("PASS: 6.7 CHUNK STORE TEST COMPLETED")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()