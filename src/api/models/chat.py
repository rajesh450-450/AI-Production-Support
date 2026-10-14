from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """
    Request received from the chat client.
    """

    message: str = Field(
        ...,
        min_length=1,
        description="User's support question.",
    )

    conversation_id: str | None = Field(
        default=None,
        description="Existing conversation ID.",
    )


class ChatResponse(BaseModel):
    """
    Response returned to the chat client.
    """

    conversation_id: str
    execution_id: str
    answer: str
    status: str

class ConversationMessage(BaseModel):
    """
    One message in a conversation.
    """

    role: str
    text: str


class ConversationHistoryResponse(BaseModel):
    """
    Conversation history returned by the API.
    """

    conversation_id: str
    messages: list[ConversationMessage]

class ConversationSummary(BaseModel):
    """
    Summary displayed in the conversation sidebar.
    """

    conversation_id: str
    title: str


class ConversationListResponse(BaseModel):
    """
    Response containing available conversations.
    """

    conversations: list[ConversationSummary]