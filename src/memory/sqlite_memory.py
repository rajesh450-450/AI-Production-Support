import json
import sqlite3
import uuid
from pathlib import Path
from typing import Any
from src.config.settings import settings
from src.memory.models import MemoryDocument


class SQLiteKnowledgeStore:
    """
    Stores durable enterprise knowledge in SQLite.

    Responsibilities:
    - Persist knowledge
    - Retrieve knowledge
    - Manage SQLite schema

    This class has no knowledge of RetrievalPipeline,
    Providers or RAG.
    """

    def __init__(
        self,
        db_path: str | None = None,
    ):

        self.db_path = Path(
            db_path or settings.sqlite_db_path
        )

        self.db_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.connection = sqlite3.connect(
            self.db_path,
            check_same_thread=False,
        )

        self.connection.row_factory = sqlite3.Row

        self._create_tables()

    # ---------------------------------------------------------
    # Database Initialization
    # ---------------------------------------------------------

    def _create_tables(self):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS knowledge
            (
                id TEXT PRIMARY KEY,
                text TEXT NOT NULL,
                metadata TEXT
            )
            """
        )

        self.connection.commit()

    # ---------------------------------------------------------
    # Add Knowledge
    # ---------------------------------------------------------

    def add(
        self,
        text: str,
        metadata: dict[str, Any] | None = None,
    ) -> str:

        document = MemoryDocument(
            id=str(uuid.uuid4()),
            text=text,
            metadata=metadata or {},
        )

        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT INTO knowledge
            (
                id,
                text,
                metadata
            )
            VALUES (?, ?, ?)
            """,
            (
                document.id,
                document.text,
                json.dumps(document.metadata),
            ),
        )

        self.connection.commit()

        return document.id

    # ---------------------------------------------------------
    # Search
    # ---------------------------------------------------------

    def search(
        self,
        query: str,
        top_k: int = 3,
    ) -> list[MemoryDocument]:

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                text,
                metadata
            FROM knowledge
            WHERE text LIKE ?
            LIMIT ?
            """,
            (
                f"%{query}%",
                top_k,
            ),
        )

        rows = cursor.fetchall()

        results: list[MemoryDocument] = []

        for row in rows:

            results.append(
                MemoryDocument(
                    id=row["id"],
                    text=row["text"],
                    metadata=json.loads(
                        row["metadata"] or "{}"
                    ),
                )
            )

        return results

    # ---------------------------------------------------------
    # Get by ID
    # ---------------------------------------------------------

    def get_by_id(
        self,
        document_id: str,
    ) -> MemoryDocument | None:

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                text,
                metadata
            FROM knowledge
            WHERE id = ?
            """,
            (document_id,),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return MemoryDocument(
            id=row["id"],
            text=row["text"],
            metadata=json.loads(
                row["metadata"] or "{}"
            ),
        )

    # ---------------------------------------------------------
    # Utility
    # ---------------------------------------------------------

    def size(self) -> int:

        cursor = self.connection.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM knowledge"
        )

        return cursor.fetchone()[0]

    def clear(self):

        cursor = self.connection.cursor()

        cursor.execute(
            "DELETE FROM knowledge"
        )

        self.connection.commit()

    def close(self):

        self.connection.close()


# =============================================================
# CONVERSATION SQLITE STORE
# =============================================================


class ConversationSQLiteStore:
    """
    Provides durable SQLite persistence for conversation messages.

    Conversation data is stored separately from enterprise
    knowledge in the same SQLite database.
    """

    def __init__(
        self,
        db_path: str | None = None,
    ):

        self.db_path = Path(
            db_path or settings.sqlite_db_path
        )

        self.db_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.connection = sqlite3.connect(
            self.db_path,
            check_same_thread=False,
        )

        self.connection.row_factory = sqlite3.Row

        self._create_table()

    # ---------------------------------------------------------
    # Database Initialization
    # ---------------------------------------------------------

    def _create_table(self):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations
            (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                text TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_conversations_conversation_id
            ON conversations(conversation_id)
            """
        )

        self.connection.commit()

    # ---------------------------------------------------------
    # Add Message
    # ---------------------------------------------------------

    def add(
        self,
        conversation_id: str,
        role: str,
        text: str,
        created_at: str,
    ) -> str:

        message_id = str(uuid.uuid4())

        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT INTO conversations
            (
                id,
                conversation_id,
                role,
                text,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                message_id,
                conversation_id,
                role,
                text,
                created_at,
            ),
        )

        self.connection.commit()

        return message_id

    # ---------------------------------------------------------
    # History
    # ---------------------------------------------------------

    def history(
        self,
        conversation_id: str,
    ) -> list[MemoryDocument]:

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                conversation_id,
                role,
                text,
                created_at
            FROM conversations
            WHERE conversation_id = ?
            ORDER BY created_at ASC
            """,
            (
                conversation_id,
            ),
        )

        rows = cursor.fetchall()

        results: list[MemoryDocument] = []

        for row in rows:

            results.append(
                MemoryDocument(
                    id=row["id"],
                    text=row["text"],
                    metadata={
                        "conversation_id": row[
                            "conversation_id"
                        ],
                        "role": row["role"],
                        "created_at": row[
                            "created_at"
                        ],
                    },
                )
            )

        return results

    # ---------------------------------------------------------
    # Recent Messages
    # ---------------------------------------------------------

    def recent(
        self,
        conversation_id: str,
        limit: int = 10,
    ) -> list[MemoryDocument]:

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                conversation_id,
                role,
                text,
                created_at
            FROM conversations
            WHERE conversation_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (
                conversation_id,
                limit,
            ),
        )

        rows = cursor.fetchall()

        rows = list(
            reversed(rows)
        )

        results: list[MemoryDocument] = []

        for row in rows:

            results.append(
                MemoryDocument(
                    id=row["id"],
                    text=row["text"],
                    metadata={
                        "conversation_id": row[
                            "conversation_id"
                        ],
                        "role": row["role"],
                        "created_at": row[
                            "created_at"
                        ],
                    },
                )
            )

        return results

    # ---------------------------------------------------------
    # List Conversations
    # ---------------------------------------------------------

    def list_conversations(self) -> list[dict]:

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT
                conversation_id,
                MIN(created_at) AS first_message_time
            FROM conversations
            GROUP BY conversation_id
            ORDER BY first_message_time ASC
            """
        )

        rows = cursor.fetchall()

        conversations = []

        for row in rows:

            conversation_id = row[
                "conversation_id"
            ]

            title_cursor = self.connection.cursor()

            title_cursor.execute(
                """
                SELECT text
                FROM conversations
                WHERE conversation_id = ?
                ORDER BY created_at ASC
                LIMIT 1
                """,
                (
                    conversation_id,
                ),
            )

            title_row = title_cursor.fetchone()

            title = (
                title_row["text"]
                if title_row
                else "New Conversation"
            )

            conversations.append(
                {
                    "conversation_id": conversation_id,
                    "title": title,
                }
            )

        return conversations

    # ---------------------------------------------------------
    # Size
    # ---------------------------------------------------------

    def size(self) -> int:

        cursor = self.connection.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM conversations"
        )

        return cursor.fetchone()[0]

    # ---------------------------------------------------------
    # Clear
    # ---------------------------------------------------------

    def clear(self):

        cursor = self.connection.cursor()

        cursor.execute(
            "DELETE FROM conversations"
        )

        self.connection.commit()

    # ---------------------------------------------------------
    # Close
    # ---------------------------------------------------------

    def close(self):

        self.connection.close()


# =============================================================
# EXISTING GLOBAL KNOWLEDGE STORE
# =============================================================

sqlite_memory = SQLiteKnowledgeStore()


# =============================================================
# GLOBAL CONVERSATION STORE
# =============================================================

conversation_sqlite_store = ConversationSQLiteStore()