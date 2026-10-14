import json
import uuid
from pathlib import Path

import faiss
import numpy as np

from src.config import settings
from src.models.embeddings import embedding_model
from src.memory.models import MemoryDocument


class SemanticMemory:
    """
    Persistent semantic memory using FAISS.

    Responsibilities:
    - Store embeddings in a FAISS index
    - Store corresponding documents and metadata
    - Persist FAISS index to disk
    - Restore FAISS index after application restart
    - Keep FAISS vector positions aligned with documents
    """

    def __init__(self):

        # -----------------------------------------------------
        # Configuration
        # -----------------------------------------------------

        self.dimension = settings.embedding_dimension

        self.storage_path = Path(
            settings.faiss_storage_path
        )

        self.storage_path.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.index_path = (
            self.storage_path / "index.faiss"
        )

        self.documents_path = (
            self.storage_path / "documents.json"
        )

        # -----------------------------------------------------
        # Initialize / Load FAISS index
        # -----------------------------------------------------

        self.index = self._load_index()

        # -----------------------------------------------------
        # Initialize / Load documents
        # -----------------------------------------------------

        self.documents = self._load_documents()

        # -----------------------------------------------------
        # Validate consistency
        # -----------------------------------------------------

        self._validate_consistency()

    # =========================================================
    # LOAD INDEX
    # =========================================================

    def _load_index(self):

        if self.index_path.exists():

            index = faiss.read_index(
                str(self.index_path)
            )

            if index.d != self.dimension:

                raise ValueError(
                    "FAISS index dimension mismatch. "
                    f"Expected {self.dimension}, "
                    f"found {index.d}."
                )

            return index

        return faiss.IndexFlatL2(
            self.dimension
        )

    # =========================================================
    # LOAD DOCUMENTS
    # =========================================================

    def _load_documents(self):

        if not self.documents_path.exists():

            return []

        with self.documents_path.open(
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

        return [
            MemoryDocument(
                id=item["id"],
                text=item["text"],
                metadata=item.get(
                    "metadata",
                    {},
                ),
            )
            for item in data
        ]

    # =========================================================
    # SAVE INDEX
    # =========================================================

    def _save_index(self):

        temp_path = (
            self.storage_path / "index.faiss.tmp"
        )

        faiss.write_index(
            self.index,
            str(temp_path),
        )

        temp_path.replace(
            self.index_path
        )

    # =========================================================
    # SAVE DOCUMENTS
    # =========================================================

    def _save_documents(self):

        temp_path = (
            self.storage_path / "documents.json.tmp"
        )

        data = [
            {
                "id": document.id,
                "text": document.text,
                "metadata": document.metadata,
            }
            for document in self.documents
        ]

        with temp_path.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=2,
            )

        temp_path.replace(
            self.documents_path
        )

    # =========================================================
    # VALIDATE CONSISTENCY
    # =========================================================

    def _validate_consistency(self):

        index_count = self.index.ntotal

        document_count = len(
            self.documents
        )

        if index_count != document_count:

            raise RuntimeError(
                "FAISS index and document store are "
                "out of sync. "
                f"FAISS vectors: {index_count}, "
                f"documents: {document_count}."
            )

    # =========================================================
    # CLEAR
    # =========================================================

    def clear(self) -> None:
        """
        Remove all semantic memory and persist
        the cleared state.
        """

        self.index.reset()

        self.documents.clear()

        self._save_index()

        self._save_documents()

    # =========================================================
    # ADD
    # =========================================================

    def add(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> str:
        """
        Generate an embedding, add it to FAISS,
        persist the document, and return its ID.
        """

        embedding = embedding_model.embed(
            text
        )

        vector = np.asarray(
            [embedding],
            dtype="float32",
        )

        # -----------------------------------------------------
        # Validate embedding dimension
        # -----------------------------------------------------

        if vector.shape[1] != self.dimension:

            raise ValueError(
                "Embedding dimension mismatch. "
                f"Expected {self.dimension}, "
                f"received {vector.shape[1]}."
            )

        # -----------------------------------------------------
        # Create document
        # -----------------------------------------------------

        document = MemoryDocument(
            id=str(uuid.uuid4()),
            text=text,
            metadata=metadata or {},
        )

        # -----------------------------------------------------
        # Add vector
        #
        # IMPORTANT:
        # FAISS index position == documents list position.
        # -----------------------------------------------------

        self.index.add(vector)

        self.documents.append(
            document
        )

        # -----------------------------------------------------
        # Persist
        # -----------------------------------------------------

        self._save_index()

        self._save_documents()

        return document.id

    # =========================================================
    # SIZE
    # =========================================================

    def size(self) -> int:

        return self.index.ntotal

    # =========================================================
    # SEARCH
    # =========================================================

    def search(
        self,
        query: str,
        top_k: int = 3,
    ) -> list[dict]:
        """
        Perform semantic similarity search.
        """

        if self.index.ntotal == 0:

            return []

        embedding = embedding_model.embed(
            query
        )

        vector = np.asarray(
            [embedding],
            dtype="float32",
        )

        # -----------------------------------------------------
        # Validate query embedding dimension
        # -----------------------------------------------------

        if vector.shape[1] != self.dimension:

            raise ValueError(
                "Query embedding dimension mismatch. "
                f"Expected {self.dimension}, "
                f"received {vector.shape[1]}."
            )

        # -----------------------------------------------------
        # Do not request more vectors than exist.
        # -----------------------------------------------------

        actual_top_k = min(
            top_k,
            self.index.ntotal,
        )

        distances, indexes = (
            self.index.search(
                vector,
                actual_top_k,
            )
        )

        results = []

        # -----------------------------------------------------
        # Preserve index / document / score relationship.
        # -----------------------------------------------------

        for idx, distance in zip(
            indexes[0],
            distances[0],
        ):

            if idx == -1:
                continue

            document = self.documents[
                int(idx)
            ]

            results.append(
                {
                    "id": document.id,
                    "text": document.text,
                    "metadata": document.metadata,
                    "score": float(distance),
                }
            )

        return results


# =============================================================
# SHARED SEMANTIC MEMORY INSTANCE
# =============================================================

semantic_memory = SemanticMemory()