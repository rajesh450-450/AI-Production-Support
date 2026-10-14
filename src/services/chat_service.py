import uuid

from src.memory.execution_context import execution_context

from src.api.models.chat import (
    ChatRequest,
    ChatResponse,
)

from src.graph.state import AgentState

from src.graph.workflow import graph

from src.memory.conversation_memory import (
    conversation_memory,
)


class ChatService:
    """
    Service layer for interactive support chat.

    Responsibilities
    ----------------
    - Receive ChatRequest
    - Create or preserve conversation ID
    - Start execution lifecycle
    - Store user message
    - Create initial AgentState
    - Invoke LangGraph workflow
    - Store assistant answer
    - Return ChatResponse

    This service does NOT:
    - Perform retrieval
    - Perform Jira lookup
    - Perform FAISS search
    - Build investigation plans
    - Execute tools
    - Review answers
    """

    def chat(
        self,
        request: ChatRequest,
    ) -> ChatResponse:

        # =================================================
        # START EXECUTION
        # =================================================

        execution_context.reset()

        # =================================================
        # CONVERSATION ID
        # =================================================

        conversation_id = (
            request.conversation_id
            or self._create_conversation_id()
        )

        execution_context.set_conversation_id(
            conversation_id
        )

        # =================================================
        # EXECUTION
        # =================================================

        try:

            # -------------------------------------------------
            # Store User Message
            # -------------------------------------------------

            conversation_memory.add(
                conversation_id=conversation_id,
                role="user",
                text=request.message,
            )

            # -------------------------------------------------
            # Initial AgentState
            # -------------------------------------------------

            initial_state: AgentState = {

                "question":
                    request.message,

                "conversation_id":
                    conversation_id,

                "context_bundle":
                    None,

                # Current plan
                "plan":
                    [],

                # All previous plans
                "plan_history":
                    [],

                # All execution evidence
                "evidence":
                    [],

                # Reviewer state
                "review_status":
                    "",

                "review_reason":
                    "",

                # Dynamic planning loop
                "planning_iteration":
                    0,

                "max_planning_iterations":
                    5,

                # Reviewer history
                "review_history":
                    [],

                # Final answer
                "answer":
                    None,
            }

            # -------------------------------------------------
            # Invoke Workflow
            # -------------------------------------------------

            result = graph.invoke(
                initial_state
            )

            # -------------------------------------------------
            # Extract Final Answer
            # -------------------------------------------------

            final_answer = result.get(
                "answer"
            )

            if final_answer is None:

                answer = ""

            elif hasattr(
                final_answer,
                "answer",
            ):

                answer = (
                    final_answer.answer
                )

            else:

                answer = str(
                    final_answer
                )

            # -------------------------------------------------
            # Store Assistant Answer
            # -------------------------------------------------

            conversation_memory.add(
                conversation_id=conversation_id,
                role="assistant",
                text=answer,
            )

            # -------------------------------------------------
            # Mark Execution Completed
            # -------------------------------------------------

            execution_context.complete()

            print(
                "\n========== METRICS =========="
            )

            print(
                execution_context.summary()
            )

            print(
                "============================="
            )

            # -------------------------------------------------
            # API Response
            # -------------------------------------------------

            return ChatResponse(
                conversation_id=
                    conversation_id,

                execution_id=
                    execution_context.get().id,

                answer=
                    answer or "",

                status=
                    "completed",
            )

        # =================================================
        # EXECUTION FAILED
        # =================================================

        except Exception:

            execution_context.fail()

            raise

    # =====================================================
    # CONVERSATION ID
    # =====================================================

    @staticmethod
    def _create_conversation_id() -> str:
        """
        Create a new unique conversation ID.
        """

        return str(
            uuid.uuid4()
        )

    # =====================================================
    # LIST CONVERSATIONS
    # =====================================================

    def list_conversations(self):
        """
        Return all available conversations.
        """

        return (
            conversation_memory
            .list_conversations()
        )