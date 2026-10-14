from src.models.llm import planner_llm

from src.prompts.builder import PromptBuilder

from src.services.retrieval_service import RetrievalService

from src.memory.execution_context import execution_context


retrieval_service = RetrievalService()

prompt_builder = PromptBuilder()


def planner_node(state):
    """
    Create the next investigation plan.

    On the first iteration:
        create the initial investigation plan.

    On subsequent iterations:
        use previous evidence and reviewer feedback
        to create a revised investigation plan.
    """

    print("\n" + "=" * 80)
    print("ENTERING PLANNER")
    print("=" * 80)

    execution_context.add_event(
        "INFO",
        "Planner",
        "Planner started.",
    )

    # ---------------------------------------------------------
    # Preserve the previous plan
    # ---------------------------------------------------------

    if state["plan"]:
        state["plan_history"].append(
            list(state["plan"])
        )

    # ---------------------------------------------------------
    # Refresh enterprise context
    # ---------------------------------------------------------

    state = retrieval_service.retrieve(state)

    context = state["context_bundle"]

    # ---------------------------------------------------------
    # Build Planner prompt
    # ---------------------------------------------------------

    prompt = prompt_builder.build_planner(
        question=state["question"],
        context=context,
        evidence=state["evidence"],
        plan_history=state["plan_history"],
        review_history=state["review_history"],
        planning_iteration=state["planning_iteration"],
    )

    print("\n")
    print("=" * 70)
    print("PLANNER CONTEXT")
    print("=" * 70)

    print(context.knowledge_context)

    print("\n")
    print("=" * 70)
    print("PLANNER PROMPT")
    print("=" * 70)

    print(prompt)

    # ---------------------------------------------------------
    # Generate plan
    # ---------------------------------------------------------

    execution_context.increment_llm_calls()

    plan = planner_llm.invoke(prompt)

    state["plan"] = plan.steps

    # ---------------------------------------------------------
    # Update progress
    # ---------------------------------------------------------

    execution_context.update_progress(
        current_phase="Planning",
        current_step=0,
        total_steps=len(plan.steps),
        current_tool="",
    )

    print("\n")
    print("=" * 70)
    print("PLANNER OUTPUT")
    print("=" * 70)

    print(plan)

    execution_context.add_event(
        "INFO",
        "Planner",
        (
            f"Investigation plan created with "
            f"{len(plan.steps)} steps."
        ),
    )

    print("\nLeaving Planner")

    execution_context.add_event(
        "INFO",
        "Planner",
        "Planner completed.",
    )

    return state