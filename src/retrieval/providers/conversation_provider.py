from src.memory.conversation_memory import ConversationMemory

from src.retrieval.models import (
    RetrievalRequest,
    RetrievalResponse,
    RetrievedDocument,
)

from src.retrieval.providers.base import RetrievalProvider


class ConversationProvider(RetrievalProvider):
    """
    Retrieves recent messages from conversation memory.

    Conversation retrieval is isolated to the requested
    conversation_id.

    Unlike knowledge retrieval, conversation history is not
    searched by semantic or keyword relevance. The most recent
    conversation messages are returned in chronological order
    so that conversational context is preserved.
    """

    def __init__(
        self,
        conversation_memory: ConversationMemory,
    ):
        self.conversation_memory = (
            conversation_memory
        )

    @property
    def provider_name(self) -> str:
        return "conversation"

    def retrieve(
        self,
        request: RetrievalRequest,
    ) -> RetrievalResponse:

        # -----------------------------------------------------
        # Extract conversation ID
        # -----------------------------------------------------

        conversation_id = (
            request.metadata.get(
                "conversation_id"
            )
            if request.metadata
            else None
        )

        # -----------------------------------------------------
        # No conversation ID
        #
        # Without a conversation ID we must not return
        # conversation data from another conversation.
        # -----------------------------------------------------

        if not conversation_id:

            return RetrievalResponse(
                documents=[]
            )

        # -----------------------------------------------------
        # Retrieve recent conversation messages
        #
        # Conversation history should preserve recent
        # conversational context rather than performing
        # keyword-based relevance search.
        # -----------------------------------------------------

        documents = (
            self.conversation_memory.recent(
                conversation_id=conversation_id,
                limit=request.top_k,
            )
        )

        # -----------------------------------------------------
        # Convert MemoryDocument -> RetrievedDocument
        # -----------------------------------------------------

        results = []

        for document in documents:

            results.append(
                RetrievedDocument(
                    id=document.id,
                    text=document.text,
                    metadata=document.metadata,
                    source=self.provider_name,
                    score=1.0,
                )
            )

        # -----------------------------------------------------
        # Return retrieval response
        # -----------------------------------------------------

        return RetrievalResponse(
            documents=results
        )