from typing import TypedDict

from src.context.models import ContextBundle
from src.models.schemas import PlanStep
from src.models.answer import FinalAnswer


class AgentState(TypedDict):
    """
    Shared business state flowing through the investigation workflow.

    Planner
        ↓
    Executor
        ↓
    Reviewer
        ↓
    Planner / Answer

    Evidence and planning history are preserved across
    dynamic re-planning iterations.

    Runtime monitoring is handled separately by ExecutionContext.
    """

    # ---------------------------------------------------------
    # User
    # ---------------------------------------------------------

    question: str
    conversation_id: str

    # ---------------------------------------------------------
    # Retrieval
    # ---------------------------------------------------------

    context_bundle: ContextBundle | None

    # ---------------------------------------------------------
    # Current Planner Output
    # ---------------------------------------------------------

    plan: list[PlanStep]

    # ---------------------------------------------------------
    # Historical Plans
    # ---------------------------------------------------------

    plan_history: list[list[PlanStep]]

    # ---------------------------------------------------------
    # Executor
    # ---------------------------------------------------------

    evidence: list

    # ---------------------------------------------------------
    # Reviewer
    # ---------------------------------------------------------

    review_status: str

    review_reason: str

    # Number of completed review/re-planning cycles.
    planning_iteration: int

    # Maximum number of Planner → Executor → Reviewer cycles.
    max_planning_iterations: int

    # Historical reviewer decisions.
    review_history: list[dict]

    # ---------------------------------------------------------
    # Answer
    # ---------------------------------------------------------

    answer: FinalAnswer | None