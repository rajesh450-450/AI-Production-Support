from src.utils.tool_executor import ToolExecutor

tool_executor = ToolExecutor()
result = tool_executor.execute(
    {
        "name": "xyz",
        "args": {}
    }
)
print(result)