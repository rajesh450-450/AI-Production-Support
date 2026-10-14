from src.graph.workflow import graph

from src.memory.execution_context import execution_context

from src.utils.profiler import (
    start_profiler,
    stop_profiler,
)


def main() -> None:

    print("\nStarting Workflow...\n")

    # ---------------------------------------------------------
    # Reset execution context
    # ---------------------------------------------------------

    execution_context.reset()

    execution_context.update_metadata(
        workflow="ProductionSupportWorkflow"
    )

    execution_context.update_progress(
        current_phase="Planning",
        current_step=0,
        total_steps=0,
        current_tool="",
    )

    execution_context.add_event(
        "INFO",
        "Workflow",
        "Investigation started.",
    )

    # ---------------------------------------------------------
    # Run workflow
    # ---------------------------------------------------------

    result = graph.invoke(
        {
            "question": (
                "Why did the Databricks Spark job fail "
                "in jira-KAN-1?"
            ),
            "context_bundle": None,
            "plan": [],
            "evidence": [],
            "answer": None,
            "review_status": "",
            "review_reason": "",
            "retry_count": 0,
        }
    )

    execution_context.complete()

    # ---------------------------------------------------------
    # Final State
    # ---------------------------------------------------------

    print()
    print("=" * 80)
    print("FINAL STATE")
    print("=" * 80)

    print(result)

    # ---------------------------------------------------------
    # Context Bundle
    # ---------------------------------------------------------

    print()
    print("=" * 80)
    print("CONTEXT BUNDLE")
    print("=" * 80)

    context_bundle = result.get(
        "context_bundle"
    )

    if context_bundle is None:

        print(
            "No context_bundle returned by workflow."
        )

    else:

        print(context_bundle)

    # ---------------------------------------------------------
    # Answer
    # ---------------------------------------------------------

    print()
    print("=" * 80)
    print("FINAL ANSWER")
    print("=" * 80)

    answer = result.get(
        "answer"
    )

    print(
        answer
        if answer is not None
        else "No answer returned."
    )

    # ---------------------------------------------------------
    # Execution Context
    # ---------------------------------------------------------

    print()
    print("=" * 80)
    print("EXECUTION CONTEXT")
    print("=" * 80)

    execution_context.display()

    print(
        execution_context.summary()
    )

    print(
        execution_context.to_dict()
    )

    # ---------------------------------------------------------
    # Workflow Diagram
    # ---------------------------------------------------------

    png = graph.get_graph().draw_mermaid_png()

    with open(
        "workflow.png",
        "wb",
    ) as file:
        file.write(png)

    print()
    print(
        "Workflow diagram saved successfully."
    )

    print(
        "\nWorkflow Finished.\n"
    )


if __name__ == "__main__":

    start_profiler()

    try:
        main()

    finally:
        stop_profiler()