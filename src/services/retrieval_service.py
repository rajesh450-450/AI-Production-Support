from src.context.builder import ContextBuilder
from src.graph.state import AgentState
from src.config.settings import settings
from src.indexing.chunk_store import ChunkStore
from src.indexing.faiss_index import FaissIndex

from src.retrieval.knowledge_retriever import KnowledgeRetriever
from src.retrieval.models import RetrievalRequest
from src.retrieval.query_understanding import QueryUnderstanding
from src.retrieval.retrieval_policy import RetrievalPolicy

from src.retrieval.providers.conversation_provider import (
    ConversationProvider,
)

from src.memory.conversation_memory import (
    conversation_memory,
)


class RetrievalService:
    """
    Enterprise Retrieval Service.

    Responsibilities
    ----------------
    - Determine whether enterprise knowledge retrieval is required
    - Always retrieve conversation context
    - Retrieve enterprise knowledge when policy allows
    - Build ContextBundle
    - Update AgentState

    Hides:
        - Query understanding
        - Retrieval policy
        - Jira exact lookup
        - FAISS semantic retrieval
        - Candidate construction
        - Deduplication
        - Ranking
        - SQLite chunk resolution
        - Conversation retrieval
        - Context assembly
    """

    def __init__(
        self,
        db_path: str | None = None,
        faiss_index_path: str | None = None,
        faiss_mapping_path: str | None = None,
    ) -> None:

        db_path = db_path or settings.sqlite_db_path
        faiss_index_path = (
            faiss_index_path
            or settings.knowledge_faiss_index_path
        )
        faiss_mapping_path = (
            faiss_mapping_path
            or settings.knowledge_faiss_mapping_path
        )
        # -------------------------------------------------
        # Knowledge Store
        # -------------------------------------------------

        self.chunk_store = ChunkStore(
            db_path=db_path
        )

        # -------------------------------------------------
        # FAISS Index
        # -------------------------------------------------

        self.faiss_index = FaissIndex(
            index_path=faiss_index_path,
            mapping_path=faiss_mapping_path,
        )

        # -------------------------------------------------
        # Query Understanding
        # -------------------------------------------------

        self.query_understanding = (
            QueryUnderstanding()
        )

        # -------------------------------------------------
        # Retrieval Policy
        # -------------------------------------------------

        self.retrieval_policy = (
            RetrievalPolicy()
        )

        # -------------------------------------------------
        # Knowledge Retriever
        # -------------------------------------------------

        self.knowledge_retriever = KnowledgeRetriever(
            chunk_store=self.chunk_store,
            query_understanding=self.query_understanding,
            faiss_index=self.faiss_index,
        )

        # -------------------------------------------------
        # Conversation Provider
        # -------------------------------------------------

        self.conversation_provider = (
            ConversationProvider(
                conversation_memory
            )
        )

        # -------------------------------------------------
        # Context Builder
        # -------------------------------------------------

        self.context_builder = ContextBuilder()

    # =====================================================
    # RETRIEVE
    # =====================================================

    def retrieve(
        self,
        state: AgentState,
    ) -> AgentState:
        """
        Retrieve context for the user query.

        Conversation retrieval ALWAYS happens.

        Enterprise knowledge retrieval happens only when
        RetrievalPolicy returns True.
        """

        query = state["question"]

        conversation_id = state[
            "conversation_id"
        ]

        documents = []

        # =================================================
        # 1. CONVERSATION RETRIEVAL
        # =================================================

        conversation_response = (
            self.conversation_provider.retrieve(
                RetrievalRequest(
                    query=query,
                    top_k=5,
                    metadata={
                        "conversation_id": conversation_id,
                    },
                )
            )
        )

        documents.extend(
            conversation_response.documents
        )

        # =================================================
        # 2. KNOWLEDGE RETRIEVAL POLICY
        # =================================================

        retrieve_knowledge = (
            self.retrieval_policy
            .should_retrieve_knowledge(
                query
            )
        )

        print(
            f"Knowledge Retrieval: "
            f"{'YES' if retrieve_knowledge else 'NO'}"
        )

        # =================================================
        # 3. ENTERPRISE KNOWLEDGE RETRIEVAL
        # =================================================

        if retrieve_knowledge:

            knowledge_response = (
                self.knowledge_retriever.retrieve(
                    RetrievalRequest(
                        query=query,
                        top_k=5,
                    )
                )
            )

            documents.extend(
                knowledge_response.documents
            )

        # =================================================
        # 4. BUILD CONTEXT
        # =================================================

        from src.retrieval.models import (
            RetrievalResponse,
        )

        combined_response = RetrievalResponse(
            documents=documents
        )

        state["context_bundle"] = (
            self.context_builder.build(
                combined_response
            )
        )

        return state