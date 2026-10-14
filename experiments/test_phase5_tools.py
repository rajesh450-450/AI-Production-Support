from src.tools.registry import registry
from src.utils.tool_executor import ToolExecutor


def test_registry():
    print("\n" + "=" * 70)
    print("TEST 1 — TOOL REGISTRY")
    print("=" * 70)

    expected_tools = {
        "add",
        "get_user_profile",
        "search_memory",
        "get_current_time",
    }

    actual_tools = set(registry.list_tools())

    print("Registered tools:")
    for tool_name in registry.list_tools():
        print(f"  - {tool_name}")

    assert actual_tools == expected_tools

    # Existing tool lookup
    add_tool = registry.get("add")
    assert add_tool is not None
    assert add_tool.name == "add"

    # Unknown tool lookup
    unknown_tool = registry.get("unknown_tool")
    assert unknown_tool is None

    print("\nRegistry lookup test: PASSED")
    print("Unknown tool test: PASSED")

    # Duplicate registration
    try:
        registry.register(add_tool)
        assert False, "Duplicate registration should have failed"

    except ValueError as ex:
        print("Duplicate registration test: PASSED")
        print(f"Expected error: {ex}")


def test_tool_executor_success():
    print("\n" + "=" * 70)
    print("TEST 2 — TOOL EXECUTOR: SUCCESS")
    print("=" * 70)

    executor = ToolExecutor()

    tool_call = {
        "name": "add",
        "args": {
            "a": 10,
            "b": 20,
        },
    }

    result = executor.execute(tool_call)

    print("Tool call:")
    print(tool_call)

    print("\nResult:")
    print(result)

    assert result["success"] is True
    assert result["result"] == 30
    assert result["error"] is None
    assert result["retryable"] is False

    print("\nTool execution success test: PASSED")


def test_tool_executor_unknown_tool():
    print("\n" + "=" * 70)
    print("TEST 3 — TOOL EXECUTOR: UNKNOWN TOOL")
    print("=" * 70)

    executor = ToolExecutor()

    tool_call = {
        "name": "unknown_tool",
        "args": {},
    }

    result = executor.execute(tool_call)

    print("Tool call:")
    print(tool_call)

    print("\nResult:")
    print(result)

    assert result["success"] is False
    assert result["retryable"] is False
    assert "Unknown tool" in result["error"]

    print("\nUnknown tool test: PASSED")


def test_tool_executor_exception():
    print("\n" + "=" * 70)
    print("TEST 4 — TOOL EXECUTOR: TOOL EXCEPTION")
    print("=" * 70)

    executor = ToolExecutor()

    # Use an existing tool but intentionally provide invalid input.
    tool_call = {
        "name": "add",
        "args": {
            "a": "invalid",
            "b": 20,
        },
    }

    result = executor.execute(tool_call)

    print("Tool call:")
    print(tool_call)

    print("\nResult:")
    print(result)

    assert result["success"] is False
    assert result["result"] is None
    assert result["error"] is not None

    print("\nTool exception test: PASSED")


def run_all_tests():
    print("\n")
    print("#" * 80)
    print("# PHASE 5 — ENTERPRISE TOOL FRAMEWORK TESTS")
    print("#" * 80)

    test_registry()
    test_tool_executor_success()
    test_tool_executor_unknown_tool()
    test_tool_executor_exception()

    print("\n")
    print("#" * 80)
    print("# ALL PHASE 5 TOOL TESTS PASSED")
    print("#" * 80)


if __name__ == "__main__":
    run_all_tests()