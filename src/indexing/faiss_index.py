import json
from pathlib import Path

import faiss
import numpy as np

from src.config.settings import settings
from src.indexing.models import DocumentChunk
from src.models.embeddings import embedding_model


class FaissIndex:
    """
    Persistent FAISS index for knowledge chunks.

    Responsibilities:
        - Convert DocumentChunk text into embeddings
        - Store embeddings in FAISS
        - Maintain vector position -> chunk_id mapping
        - Persist and reload the FAISS index

    FAISS is a derived index.
    SQLite remains the canonical source of chunk information.
    """

    def __init__(
        self,
        index_path: str | None = None,
        mapping_path: str | None = None,
        dimension: int | None = None,
    ) -> None:

        self.index_path = Path(
            index_path
            or settings.knowledge_faiss_index_path
        )

        self.mapping_path = Path(
            mapping_path
            or settings.knowledge_faiss_mapping_path
        )

        self.dimension = (
            dimension
            if dimension is not None
            else settings.embedding_dimension
        )

        self.index_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.mapping_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if (
            self.index_path.exists()
            and self.mapping_path.exists()
        ):

            self.index = faiss.read_index(
                str(self.index_path)
            )

            with open(
                self.mapping_path,
                "r",
                encoding="utf-8",
            ) as file:

                self.chunk_ids: list[str] = json.load(
                    file
                )

        else:

            self.index = faiss.IndexFlatL2(
                self.dimension
            )

            self.chunk_ids: list[str] = []

    # ============================================================
    # RESET
    # ============================================================

    def clear(self) -> None:
        """
        Remove all vectors and chunk mappings.
        """

        self.index.reset()

        self.chunk_ids.clear()

    # ============================================================
    # ADD ONE CHUNK
    # ============================================================

    def add(
        self,
        chunk: DocumentChunk,
    ) -> None:
        """
        Embed and add one DocumentChunk to FAISS.
        """

        embedding = embedding_model.embed(
            chunk.text
        )

        vector = np.asarray(
            [embedding],
            dtype="float32",
        )

        if vector.shape != (
            1,
            self.dimension,
        ):

            raise ValueError(
                "Embedding dimension mismatch. "
                f"Expected {self.dimension}, "
                f"received {vector.shape[1]}."
            )

        self.index.add(vector)

        self.chunk_ids.append(
            chunk.chunk_id
        )

    # ============================================================
    # ADD MANY CHUNKS
    # ============================================================

    def add_chunks(
        self,
        chunks: list[DocumentChunk],
    ) -> None:
        """
        Embed and add multiple DocumentChunk objects.
        """

        for chunk in chunks:

            self.add(chunk)

    # ============================================================
    # SIZE
    # ============================================================

    def size(self) -> int:
        """
        Return the number of vectors stored in FAISS.
        """

        return self.index.ntotal

    # ============================================================
    # GET CHUNK ID BY VECTOR POSITION
    # ============================================================

    def get_chunk_id(
        self,
        vector_index: int,
    ) -> str:
        """
        Return the chunk_id associated with a FAISS vector.
        """

        return self.chunk_ids[
            vector_index
        ]

    # ============================================================
    # SAVE
    # ============================================================

    def save(self) -> None:
        """
        Persist FAISS index and vector-to-chunk mapping.
        """

        faiss.write_index(
            self.index,
            str(self.index_path),
        )

        with open(
            self.mapping_path,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                self.chunk_ids,
                file,
                ensure_ascii=False,
                indent=2,
            )

    # ============================================================
    # VALIDATION
    # ============================================================

    def validate(self) -> None:
        """
        Validate FAISS vector count and mapping count.
        """

        if self.index.ntotal != len(
            self.chunk_ids
        ):

            raise ValueError(
                "FAISS vector count does not match "
                "chunk_id mapping count."
            )

    # ============================================================
    # SEARCH
    # ============================================================

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict]:
        """
        Perform semantic search and return chunk IDs
        with their FAISS distances.
        """

        embedding = embedding_model.embed(
            query
        )

        vector = np.asarray(
            [embedding],
            dtype="float32",
        )

        if vector.shape != (
            1,
            self.dimension,
        ):

            raise ValueError(
                "Embedding dimension mismatch. "
                f"Expected {self.dimension}, "
                f"received {vector.shape[1]}."
            )

        distances, indexes = (
            self.index.search(
                vector,
                top_k,
            )
        )

        results = []

        for distance, index in zip(
            distances[0],
            indexes[0],
        ):

            if index == -1:
                continue

            results.append(
                {
                    "chunk_id": self.get_chunk_id(
                        int(index)
                    ),
                    "score": float(distance),
                }
            )

        return results