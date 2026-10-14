import json
import sqlite3
from pathlib import Path
from typing import Any

from src.indexing.models import DocumentChunk


class ChunkStore:
    """
    Durable SQLite store for indexed DocumentChunk objects.

    SQLite is the canonical source of truth for:
        - chunk content
        - chunk identity
        - parent document identity
        - source metadata
        - chunk ordering
        - additional metadata

    FAISS is a derived semantic index and is not responsible
    for being the authoritative store of chunk information.
    """

    def __init__(
        self,
        db_path: str = "data/knowledge.db",
    ) -> None:

        self.db_path = Path(db_path)

        self.db_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        # -------------------------------------------------
        # Create database and tables
        # -------------------------------------------------

        with self._connect() as connection:

            self._create_tables(
                connection
            )

    # ============================================================
    # CONNECTION
    # ============================================================

    def _connect(self) -> sqlite3.Connection:
        """
        Create a new SQLite connection.

        A new connection is created for each database operation.
        This makes ChunkStore safe to use from FastAPI worker threads.
        """

        connection = sqlite3.connect(
            self.db_path
        )

        connection.row_factory = sqlite3.Row

        return connection

    # ============================================================
    # DATABASE INITIALIZATION
    # ============================================================

    def _create_tables(
        self,
        connection: sqlite3.Connection,
    ) -> None:

        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS chunks
            (
                chunk_id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                source TEXT NOT NULL,
                external_id TEXT NOT NULL,
                title TEXT NOT NULL,
                text TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                metadata TEXT
            )
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_chunks_document_id
            ON chunks(document_id)
            """
        )

        connection.commit()

    # ============================================================
    # ADD
    # ============================================================

    def add(
        self,
        chunk: DocumentChunk,
    ) -> None:
        """
        Persist one DocumentChunk.

        chunk_id is the stable primary key.
        """

        with self._connect() as connection:

            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO chunks
                (
                    chunk_id,
                    document_id,
                    source,
                    external_id,
                    title,
                    text,
                    chunk_index,
                    metadata
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    chunk.chunk_id,
                    chunk.document_id,
                    chunk.source,
                    chunk.external_id,
                    chunk.title,
                    chunk.text,
                    chunk.chunk_index,
                    json.dumps(
                        chunk.metadata,
                        ensure_ascii=False,
                    ),
                ),
            )

            connection.commit()

    # ============================================================
    # UPSERT
    # ============================================================

    def upsert(
        self,
        chunk: DocumentChunk,
    ) -> None:
        """
        Insert a chunk or replace the existing chunk with
        the same chunk_id.

        Useful for re-indexing updated source documents.
        """

        with self._connect() as connection:

            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO chunks
                (
                    chunk_id,
                    document_id,
                    source,
                    external_id,
                    title,
                    text,
                    chunk_index,
                    metadata
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)

                ON CONFLICT(chunk_id)
                DO UPDATE SET
                    document_id = excluded.document_id,
                    source = excluded.source,
                    external_id = excluded.external_id,
                    title = excluded.title,
                    text = excluded.text,
                    chunk_index = excluded.chunk_index,
                    metadata = excluded.metadata
                """,
                (
                    chunk.chunk_id,
                    chunk.document_id,
                    chunk.source,
                    chunk.external_id,
                    chunk.title,
                    chunk.text,
                    chunk.chunk_index,
                    json.dumps(
                        chunk.metadata,
                        ensure_ascii=False,
                    ),
                ),
            )

            connection.commit()

    # ============================================================
    # GET BY CHUNK ID
    # ============================================================

    def get_by_id(
        self,
        chunk_id: str,
    ) -> DocumentChunk | None:

        with self._connect() as connection:

            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT
                    chunk_id,
                    document_id,
                    source,
                    external_id,
                    title,
                    text,
                    chunk_index,
                    metadata
                FROM chunks
                WHERE chunk_id = ?
                """,
                (chunk_id,),
            )

            row = cursor.fetchone()

            if row is None:
                return None

            return self._row_to_chunk(row)

    # ============================================================
    # GET BY DOCUMENT ID
    # ============================================================

    def get_by_document_id(
        self,
        document_id: str,
    ) -> list[DocumentChunk]:

        with self._connect() as connection:

            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT
                    chunk_id,
                    document_id,
                    source,
                    external_id,
                    title,
                    text,
                    chunk_index,
                    metadata
                FROM chunks
                WHERE document_id = ?
                ORDER BY chunk_index
                """,
                (document_id,),
            )

            rows = cursor.fetchall()

            return [
                self._row_to_chunk(row)
                for row in rows
            ]

    # ============================================================
    # GET ALL
    # ============================================================

    def get_all(self) -> list[DocumentChunk]:
        """
        Return all indexed chunks in deterministic order.

        SQLite is the canonical source of chunk information.
        """

        with self._connect() as connection:

            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT
                    chunk_id,
                    document_id,
                    source,
                    external_id,
                    title,
                    text,
                    chunk_index,
                    metadata
                FROM chunks
                ORDER BY document_id, chunk_index
                """
            )

            rows = cursor.fetchall()

            return [
                self._row_to_chunk(row)
                for row in rows
            ]

    # ============================================================
    # DELETE BY DOCUMENT ID
    # ============================================================

    def delete_by_document_id(
        self,
        document_id: str,
    ) -> int:

        with self._connect() as connection:

            cursor = connection.cursor()

            cursor.execute(
                """
                DELETE FROM chunks
                WHERE document_id = ?
                """,
                (document_id,),
            )

            deleted_count = cursor.rowcount

            connection.commit()

            return deleted_count

    # ============================================================
    # SIZE
    # ============================================================

    def size(self) -> int:

        with self._connect() as connection:

            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM chunks
                """
            )

            return int(
                cursor.fetchone()[0]
            )

    # ============================================================
    # CLEAR
    # ============================================================

    def clear(self) -> None:

        with self._connect() as connection:

            cursor = connection.cursor()

            cursor.execute(
                """
                DELETE FROM chunks
                """
            )

            connection.commit()

    # ============================================================
    # CLOSE
    # ============================================================

    def close(self) -> None:
        """
        No persistent connection is maintained.

        Kept for API compatibility with existing callers.
        """

        pass

    # ============================================================
    # INTERNAL CONVERSION
    # ============================================================

    @staticmethod
    def _row_to_chunk(
        row: sqlite3.Row,
    ) -> DocumentChunk:

        metadata: dict[str, Any] = json.loads(
            row["metadata"] or "{}"
        )

        return DocumentChunk(
            chunk_id=row["chunk_id"],
            document_id=row["document_id"],
            source=row["source"],
            external_id=row["external_id"],
            title=row["title"],
            text=row["text"],
            chunk_index=row["chunk_index"],
            metadata=metadata,
        )