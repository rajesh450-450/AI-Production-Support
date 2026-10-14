from src.config import settings
from src.indexing.chunker import DocumentChunker
from src.indexing.chunk_store import ChunkStore
from src.indexing.faiss_index import FaissIndex
from src.indexing.pipeline import IndexingSourcePipeline
from src.indexing.sources.confluence import ConfluenceSource
from src.indexing.sources.jira import JiraSource
from src.utils.profiler import (
    start_profiler,
    stop_profiler,
)


class KnowledgeIndexer:
    """
    Independent knowledge indexing pipeline.

    Flow:

        External Sources
            ↓
        SourceDocument
            ↓
        DocumentChunk
            ↓
        SQLite ChunkStore
            ↓
        Read all chunks from SQLite
            ↓
        FAISS

    SQLite is the canonical source of chunk information.
    FAISS is a derived semantic index.
    """

    def __init__(
        self,
        pipeline: IndexingSourcePipeline,
        chunker: DocumentChunker,
        chunk_store: ChunkStore,
        faiss_index: FaissIndex,
    ) -> None:
        self.pipeline = pipeline
        self.chunker = chunker
        self.chunk_store = chunk_store
        self.faiss_index = faiss_index

    def run(self) -> dict[str, int]:
        """
        Load, chunk, persist to SQLite, and rebuild FAISS.

        Each indexing run performs a complete rebuild:

        1. Clear existing SQLite chunks.
        2. Load source documents.
        3. Create new chunks.
        4. Persist chunks to SQLite.
        5. Rebuild FAISS from the complete SQLite dataset.

        SQLite is the canonical source.
        FAISS is a derived semantic index.
        """

        # ----------------------------------------------------
        # Clear existing knowledge
        #
        # SQLite is the canonical source of chunk information.
        # Every indexing run starts with a clean knowledge set.
        # ----------------------------------------------------

        self.chunk_store.clear()

        # ----------------------------------------------------
        # Load source documents
        # ----------------------------------------------------

        documents = self.pipeline.load()

        # ----------------------------------------------------
        # Create chunks
        # ----------------------------------------------------

        chunks = self.chunker.chunk_documents(
            documents
        )

        # ----------------------------------------------------
        # Persist chunks to SQLite
        # ----------------------------------------------------

        for chunk in chunks:
            self.chunk_store.upsert(chunk)

        # ----------------------------------------------------
        # Read complete canonical chunk set from SQLite
        # ----------------------------------------------------

        all_chunks = self.chunk_store.get_all()

        # ----------------------------------------------------
        # Rebuild FAISS from SQLite
        # ----------------------------------------------------

        self.faiss_index.clear()

        self.faiss_index.add_chunks(
            all_chunks
        )

        # ----------------------------------------------------
        # Validate FAISS
        # ----------------------------------------------------

        self.faiss_index.validate()

        # ----------------------------------------------------
        # Persist FAISS index and mapping
        # ----------------------------------------------------

        self.faiss_index.save()

        return {
            "documents": len(documents),
            "chunks": len(chunks),
            "stored_chunks": len(all_chunks),
            "faiss_vectors": self.faiss_index.size(),
        }


def run_indexing() -> None:
    """
    Execute the complete knowledge indexing process.

    All infrastructure paths are loaded from application
    configuration rather than being hard-coded here.
    """

    # --------------------------------------------------------
    # Source pipeline
    # --------------------------------------------------------

    pipeline = IndexingSourcePipeline(
        sources=[
            ConfluenceSource(),
            JiraSource(),
        ]
    )

    # --------------------------------------------------------
    # Chunking
    # --------------------------------------------------------

    chunker = DocumentChunker(
        chunk_size=1000,
        chunk_overlap=150,
    )

    # --------------------------------------------------------
    # Persistent knowledge store
    #
    # SQLite is the canonical source of chunk information.
    # Path comes from application configuration.
    # --------------------------------------------------------

    chunk_store = ChunkStore(
        db_path=settings.sqlite_db_path
    )

    # --------------------------------------------------------
    # FAISS semantic index
    #
    # FAISS paths come from application configuration.
    # --------------------------------------------------------

    faiss_index = FaissIndex(
        index_path=settings.knowledge_faiss_index_path,
        mapping_path=settings.knowledge_faiss_mapping_path,
    )

    # --------------------------------------------------------
    # Create indexer
    # --------------------------------------------------------

    indexer = KnowledgeIndexer(
        pipeline=pipeline,
        chunker=chunker,
        chunk_store=chunk_store,
        faiss_index=faiss_index,
    )

    # --------------------------------------------------------
    # Execute indexing
    # --------------------------------------------------------

    try:
        result = indexer.run()

        print()
        print("Knowledge indexing completed.")
        print(f"Documents loaded : {result['documents']}")
        print(f"Chunks generated : {result['chunks']}")
        print(f"Chunks in SQLite : {result['stored_chunks']}")
        print(f"FAISS vectors    : {result['faiss_vectors']}")

    finally:
        chunk_store.close()


if __name__ == "__main__":
    start_profiler()

    try:
        run_indexing()
    finally:
        stop_profiler()