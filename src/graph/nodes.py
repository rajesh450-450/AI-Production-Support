from src.memory.execution_context import execution_context


def review_router(state):
    """
    Decide the next workflow node after Reviewer.

    success
        -> Answer

    retry
        -> Planner

    If the maximum planning iterations are exhausted,
    send the available evidence to Answer rather than
    continuing indefinitely.
    """

    print("\n" + "=" * 80)
    print("ENTERING ROUTER")
    print("=" * 80)

    print("\n" + "=" * 70)
    print("ROUTER")
    print("=" * 70)

    print(
        f"Status              : "
        f"{state['review_status']}"
    )

    print(
        f"Reason              : "
        f"{state['review_reason']}"
    )

    print(
        f"Planning Iteration  : "
        f"{state['planning_iteration']}"
    )

    print(
        f"Maximum Iterations  : "
        f"{state['max_planning_iterations']}"
    )

    # ---------------------------------------------------------
    # Reviewer accepted the investigation
    # ---------------------------------------------------------

    if state["review_status"] == "success":

        print(
            "\nInvestigation completed successfully."
        )

        execution_context.add_event(
            "INFO",
            "Router",
            "Reviewer accepted the investigation. "
            "Routing to Answer.",
        )

        return "success"

    # ---------------------------------------------------------
    # Maximum iterations reached
    # ---------------------------------------------------------

    if (
        state["planning_iteration"]
        >= state["max_planning_iterations"]
    ):

        print(
            "\nMaximum planning iterations reached."
        )

        execution_context.add_event(
            "WARNING",
            "Router",
            "Maximum planning iterations reached. "
            "Routing to Answer with available evidence.",
        )

        return "max_iterations"

    # ---------------------------------------------------------
    # Dynamic re-planning
    # ---------------------------------------------------------

    print(
        "\nReviewer requested additional evidence."
    )

    print(
        "Routing back to Planner."
    )

    execution_context.add_event(
        "INFO",
        "Router",
        "Reviewer requested additional evidence. "
        "Routing back to Planner.",
    )

    return "retry"