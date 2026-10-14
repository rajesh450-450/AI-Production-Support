from src.tools.registry import registry
from src.memory.execution_context import execution_context


class ToolExecutor:
    """
    Controlled execution boundary for all tools.

    Responsibilities
    ----------------
    - Resolve registered tools
    - Execute tools
    - Track tool execution metrics
    - Record tool execution events
    - Determine whether failures are retryable
    """

    def execute(self, tool_call):

        tool_name = tool_call["name"]
        tool_args = tool_call.get(
            "args",
            {},
        )

        # ---------------------------------------------------------
        # Tool Lookup
        # ---------------------------------------------------------

        tool = registry.get(
            tool_name
        )

        if tool is None:

            execution_context.add_event(
                level="ERROR",
                component=tool_name,
                message="Tool lookup failed. Unknown tool.",
            )

            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}",
                "retryable": False,
            }

        # ---------------------------------------------------------
        # Tool Execution Started
        # ---------------------------------------------------------

        execution_context.add_event(
            level="INFO",
            component=tool_name,
            message="Tool execution started.",
        )

        # ---------------------------------------------------------
        # Tool Execution
        # ---------------------------------------------------------

        try:

            execution_context.increment_tool_calls()

            result = tool.invoke(
                tool_args
            )

            # -----------------------------------------------------
            # Tool Execution Completed
            # -----------------------------------------------------

            execution_context.add_event(
                level="INFO",
                component=tool_name,
                message="Tool execution completed.",
            )

            return {
                "success": True,
                "result": result,
                "error": None,
                "retryable": False,
            }

        except Exception as ex:

            message = str(ex).lower()

            retryable = any(
                keyword in message
                for keyword in [
                    "timeout",
                    "temporarily",
                    "connection",
                    "network",
                    "429",
                    "500",
                    "503",
                ]
            )

            # -----------------------------------------------------
            # Tool Execution Failed
            # -----------------------------------------------------

            execution_context.add_event(
                level="ERROR",
                component=tool_name,
                message="Tool execution failed.",
            )

            return {
                "success": False,
                "result": None,
                "error": str(ex),
                "retryable": retryable,
            }