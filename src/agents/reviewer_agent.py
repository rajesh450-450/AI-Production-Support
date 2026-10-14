from src.models.llm import reviewer_llm

from src.prompts.reviewer import REVIEWER_PROMPT

from src.memory.execution_context import execution_context


def reviewer_node(state):
    """
    Review all evidence collected so far.

    The Reviewer does not create a new plan.

    It only determines:

        success -> Answer
        retry   -> Planner
    """

    print("\n" + "=" * 80)
    print("ENTERING REVIEWER")
    print("=" * 80)

    execution_context.add_event(
        "INFO",
        "Reviewer",
        "Reviewer started.",
    )

    prompt = f"""
{REVIEWER_PROMPT}

==================================================
PLANNING ITERATION
==================================================

{state["planning_iteration"]}

==================================================
QUESTION
==================================================

{state["question"]}

==================================================
RELEVANT KNOWLEDGE
==================================================

{state["context_bundle"].knowledge_context}

==================================================
CURRENT PLAN
==================================================

{state["plan"]}

==================================================
PREVIOUS PLANS
==================================================

{state["plan_history"]}

==================================================
EVIDENCE COLLECTED SO FAR
==================================================

{state["evidence"]}

==================================================
PREVIOUS REVIEW DECISIONS
==================================================

{state["review_history"]}
"""

    execution_context.update_progress(
        current_phase="Review",
        current_tool="",
    )

    print("\n" + "=" * 70)
    print("REVIEWER")
    print("=" * 70)

    print("\n----- REVIEWER PROMPT -----")
    print(prompt)

    execution_context.increment_llm_calls()

    review = reviewer_llm.invoke(prompt)

    print("\n----- REVIEW DECISION -----")
    print(review)

    state["review_status"] = review.status

    state["review_reason"] = review.reason

    # ---------------------------------------------------------
    # Store review history
    # ---------------------------------------------------------

    state["review_history"].append(
        {
            "iteration": state[
                "planning_iteration"
            ],
            "status": review.status,
            "reason": review.reason,
        }
    )

    # ---------------------------------------------------------
    # Retry means another planning iteration
    # ---------------------------------------------------------

    if review.status == "retry":

        state["planning_iteration"] += 1

        execution_context.add_event(
            "INFO",
            "Reviewer",
            (
                "Investigation requires another "
                "planning iteration."
            ),
        )

    else:

        execution_context.add_event(
            "INFO",
            "Reviewer",
            "Investigation completed successfully.",
        )

    print("\nLeaving Reviewer")

    execution_context.add_event(
        "INFO",
        "Reviewer",
        "Reviewer completed.",
    )

    return state