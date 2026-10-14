from langgraph.graph import END, StateGraph

from src.graph.state import AgentState

from src.graph.nodes import review_router

from src.agents.planner_agent import planner_node
from src.agents.investigator_agent import executor_node
from src.agents.reviewer_agent import reviewer_node
from src.agents.answer_agent import answer_node


def create_graph():
    """
    Build and compile the enterprise investigation workflow.

    Workflow:

        Planner
            ↓
        Executor
            ↓
        Reviewer
            ↓
        ┌───────────────┬───────────────────┐
        │               │                   │
      success          retry          max iterations
        │               │                   │
        ▼               ▼                   ▼
      Answer          Planner             Answer
        │               │                   │
        └───────────────┴───────────────────┘
                        ↓
                       END

    This module only constructs the graph.
    """

    builder = StateGraph(
        AgentState
    )

    # ---------------------------------------------------------
    # Nodes
    # ---------------------------------------------------------

    builder.add_node(
        "planner",
        planner_node,
    )

    builder.add_node(
        "executor",
        executor_node,
    )

    builder.add_node(
        "reviewer",
        reviewer_node,
    )

    builder.add_node(
        "answer",
        answer_node,
    )

    # ---------------------------------------------------------
    # Initial flow
    # ---------------------------------------------------------

    builder.set_entry_point(
        "planner"
    )

    builder.add_edge(
        "planner",
        "executor",
    )

    builder.add_edge(
        "executor",
        "reviewer",
    )

    # ---------------------------------------------------------
    # Dynamic review routing
    # ---------------------------------------------------------

    builder.add_conditional_edges(
        "reviewer",
        review_router,
        {
            "success": "answer",
            "retry": "planner",
            "max_iterations": "answer",
        },
    )

    # ---------------------------------------------------------
    # End
    # ---------------------------------------------------------

    builder.add_edge(
        "answer",
        END,
    )

    return builder.compile()


graph = create_graph()