import re
from datetime import datetime, timezone

from src.memory.models import MemoryDocument

from src.memory.sqlite_memory import (
    conversation_sqlite_store,
)


class ConversationMemory:
    """
    Stores conversational history.

    Conversation history is isolated by conversation_id.

    SQLite is the durable source of truth.

    The in-memory documents list is retained as a
    lightweight runtime cache.
    """

    def __init__(self):

        self.documents: list[MemoryDocument] = []

    # ---------------------------------------------------------
    # Add Conversation
    # ---------------------------------------------------------

    def add(
        self,
        conversation_id: str,
        role: str,
        text: str,
    ) -> None:
        """
        Store one conversation message.

        The message is persisted to SQLite and also
        kept in memory for the current process.
        """

        created_at = (
            datetime.now(timezone.utc).isoformat()
        )

        document = MemoryDocument(
            id="",
            text=text,
            metadata={
                "conversation_id": conversation_id,
                "role": role,
                "created_at": created_at,
            },
        )

        # -----------------------------------------------------
        # Persist to SQLite
        # -----------------------------------------------------

        message_id = conversation_sqlite_store.add(
            conversation_id=conversation_id,
            role=role,
            text=text,
            created_at=created_at,
        )

        # -----------------------------------------------------
        # Update runtime document
        # -----------------------------------------------------

        document.id = message_id

        self.documents.append(
            document
        )

    # ---------------------------------------------------------
    # Internal Tokenizer
    # ---------------------------------------------------------

    @staticmethod
    def _tokenize(
        text: str,
    ) -> set[str]:

        return set(
            re.findall(
                r"\b[a-z0-9]+\b",
                text.lower(),
            )
        )

    # ---------------------------------------------------------
    # Search
    # ---------------------------------------------------------

    def search(
        self,
        conversation_id: str,
        query: str,
        top_k: int = 3,
    ) -> list[MemoryDocument]:
        """
        Search only within the specified conversation.

        Uses the persisted conversation history.
        """

        documents = self.history(
            conversation_id
        )

        query_tokens = self._tokenize(
            query
        )

        matches = []

        for document in documents:

            document_tokens = self._tokenize(
                document.text
            )

            if query_tokens.intersection(
                document_tokens
            ):

                matches.append(
                    document
                )

            if len(matches) >= top_k:
                break

        return matches

    # ---------------------------------------------------------
    # Recent Messages
    # ---------------------------------------------------------

    def recent(
        self,
        conversation_id: str,
        limit: int = 10,
    ) -> list[MemoryDocument]:
        """
        Return recent messages for one conversation.
        """

        return conversation_sqlite_store.recent(
            conversation_id=conversation_id,
            limit=limit,
        )

    # ---------------------------------------------------------
    # Full Conversation History
    # ---------------------------------------------------------

    def history(
        self,
        conversation_id: str,
    ) -> list[MemoryDocument]:
        """
        Return all messages for one conversation
        in chronological order.
        """

        return conversation_sqlite_store.history(
            conversation_id=conversation_id
        )

    # ---------------------------------------------------------
    # List Conversations
    # ---------------------------------------------------------

    def list_conversations(self) -> list[dict]:
        """
        Return all persisted conversations with
        a simple display title.
        """

        return conversation_sqlite_store.list_conversations()

    # ---------------------------------------------------------
    # Utilities
    # ---------------------------------------------------------

    def size(self) -> int:

        return conversation_sqlite_store.size()

    def clear(self) -> None:

        # Clear durable storage.
        conversation_sqlite_store.clear()

        # Clear runtime cache.
        self.documents.clear()


# =============================================================
# GLOBAL CONVERSATION MEMORY
# =============================================================

conversation_memory = ConversationMemory()