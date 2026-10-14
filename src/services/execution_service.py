import sys

sys.stdout.reconfigure(
    encoding="utf-8"
)

from src.models.llm import executor_llm

from src.memory.execution_context import execution_context

from src.prompts.builder import PromptBuilder

from src.utils.tool_executor import ToolExecutor


class ExecutionService:
    """
    Executes one investigation step.

    Responsibilities
    ----------------
    - Build executor prompt
    - Invoke Executor LLM
    - Validate requested tool against the plan
    - Execute valid tools
    - Record evidence
    - Update ExecutionContext

    This service NEVER:
    - Performs retrieval
    - Creates plans
    - Reviews answers
    """

    def __init__(self):

        self.prompt_builder = PromptBuilder()

        self.tool_executor = ToolExecutor()

    # ---------------------------------------------------------
    # Execute One Step
    # ---------------------------------------------------------

    def execute(
        self,
        state,
        step,
    ):

        execution_context.update_progress(
            current_phase="Executor",
            current_step=step.step,
            current_tool=step.tool or "",
        )

        # -----------------------------------------------------
        # Build prompt
        # -----------------------------------------------------

        prompt = self.prompt_builder.build_executor(
            question=state["question"],
            context=state["context_bundle"],
            step=step,
            evidence=state["evidence"],
        )

        print("\n----- EXECUTOR PROMPT -----")
        print(prompt)

        # -----------------------------------------------------
        # Invoke Executor
        # -----------------------------------------------------

        execution_context.increment_llm_calls()

        ai_message = executor_llm.invoke(prompt)

        print("\n----- AI MESSAGE -----")
        print(ai_message)

        tool_results = []

        # =====================================================
        # TOOL STEP
        # =====================================================

        if step.type == "tool":

            expected_tool = step.tool

            if not expected_tool:

                tool_results.append(
                    {
                        "tool": None,
                        "args": {},
                        "result": {
                            "success": False,
                            "result": None,
                            "error": (
                                "Planner created a tool step "
                                "without specifying a tool."
                            ),
                            "retryable": True,
                        },
                    }
                )

            elif not ai_message.tool_calls:

                print(
                    "\nNo tool call was produced "
                    "for the required tool step."
                )

                tool_results.append(
                    {
                        "tool": expected_tool,
                        "args": {},
                        "result": {
                            "success": False,
                            "result": None,
                            "error": (
                                f"Expected tool '{expected_tool}' "
                                "but Executor produced no tool call."
                            ),
                            "retryable": True,
                        },
                    }
                )

                execution_context.add_event(
                    level="WARNING",
                    component="Executor",
                    message=(
                        f"Expected tool '{expected_tool}' "
                        "was not called."
                    ),
                )

            else:

                print(
                    "\n----- EXECUTING TOOLS -----"
                )

                for tool_call in ai_message.tool_calls:

                    actual_tool = tool_call["name"]

                    # -------------------------------------------------
                    # Safety validation
                    # -------------------------------------------------

                    if actual_tool != expected_tool:

                        print(
                            f"Rejected unexpected tool: "
                            f"{actual_tool}"
                        )

                        result = {
                            "success": False,
                            "result": None,
                            "error": (
                                f"Unexpected tool '{actual_tool}'. "
                                f"Expected '{expected_tool}'."
                            ),
                            "retryable": True,
                        }

                        tool_results.append(
                            {
                                "tool": actual_tool,
                                "args": tool_call.get(
                                    "args",
                                    {},
                                ),
                                "result": result,
                            }
                        )

                        execution_context.add_event(
                            level="WARNING",
                            component="Executor",
                            message=(
                                f"Rejected unexpected tool "
                                f"'{actual_tool}' for step "
                                f"{step.step}; expected "
                                f"'{expected_tool}'."
                            ),
                        )

                        continue

                    # -------------------------------------------------
                    # Execute expected tool
                    # -------------------------------------------------

                    execution_context.update_progress(
                        current_tool=actual_tool,
                    )

                    result = self.tool_executor.execute(
                        tool_call
                    )

                    print(
                        f"{actual_tool}"
                        f"({tool_call['args']}) = "
                        f"{result}"
                    )

                    tool_results.append(
                        {
                            "tool": actual_tool,
                            "args": tool_call.get(
                                "args",
                                {},
                            ),
                            "result": result,
                        }
                    )

        # =====================================================
        # NON-TOOL STEP
        # =====================================================

        else:

            if ai_message.tool_calls:

                print(
                    "\nUnexpected tool call produced "
                    "for non-tool step."
                )

                for tool_call in ai_message.tool_calls:

                    actual_tool = tool_call["name"]

                    tool_results.append(
                        {
                            "tool": actual_tool,
                            "args": tool_call.get(
                                "args",
                                {},
                            ),
                            "result": {
                                "success": False,
                                "result": None,
                                "error": (
                                    f"Tool '{actual_tool}' "
                                    f"was not expected for "
                                    f"step {step.step}."
                                ),
                                "retryable": True,
                            },
                        }
                    )

                execution_context.add_event(
                    level="WARNING",
                    component="Executor",
                    message=(
                        f"Unexpected tool call generated "
                        f"for non-tool step {step.step}."
                    ),
                )

            else:

                print("\nNo tools executed.")

                execution_context.add_event(
                    level="INFO",
                    component="Executor",
                    message="No tool execution required.",
                )

        # -----------------------------------------------------
        # Store evidence
        # -----------------------------------------------------

        evidence_entry = {
            "step": step.description,
            "step_number": step.step,
            "type": step.type,
            "expected_tool": step.tool,
            "llm_output": ai_message.content,
            "tool_results": tool_results,
        }

        state["evidence"].append(
            evidence_entry
        )

        return state