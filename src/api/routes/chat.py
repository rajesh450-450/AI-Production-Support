from fastapi import APIRouter

from src.api.models.chat import (
    ChatRequest,
    ChatResponse,
    ConversationHistoryResponse,
    ConversationMessage,
    ConversationListResponse,
)

from src.services.chat_service import ChatService

from src.memory.conversation_memory import (
    conversation_memory,
)


router = APIRouter()

chat_service = ChatService()


@router.post(
    "/chat",
    response_model=ChatResponse,
)
def chat(
    request: ChatRequest,
) -> ChatResponse:
    """
    Handle an interactive support chat request.
    """

    return chat_service.chat(
        request
    )

@router.get(
    "/chat/{conversation_id}/history",
    response_model=ConversationHistoryResponse,
)
def get_conversation_history(
    conversation_id: str,
) -> ConversationHistoryResponse:
    """
    Return the complete message history for a conversation.
    """

    documents = conversation_memory.history(
        conversation_id=conversation_id
    )

    messages = [
        ConversationMessage(
            role=document.metadata.get(
                "role",
                "",
            ),
            text=document.text,
        )
        for document in documents
    ]

    return ConversationHistoryResponse(
        conversation_id=conversation_id,
        messages=messages,
    )

@router.get(
    "/chat/conversations",
    response_model=ConversationListResponse,
)
def list_conversations() -> ConversationListResponse:
    """
    Return all available conversations.
    """

    conversations = (
        chat_service.list_conversations()
    )

    return ConversationListResponse(
        conversations=conversations
    )