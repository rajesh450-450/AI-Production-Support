class ToolRegistry:
    """
    Stores all available tools and provides lookup by tool name.
    """

    def __init__(self):
        self.tools = {}

    def register(self, tool):
        """Register a valid tool."""
        if not hasattr(tool, "name") or not hasattr(tool, "invoke"):
            raise ValueError("Invalid tool. Tool must have name and invoke().")

        if tool.name in self.tools:
            raise ValueError(
                f"Tool '{tool.name}' is already registered."
            )

        self.tools[tool.name] = tool

    def get(self, tool_name):
        """Return a tool by name."""
        return self.tools.get(tool_name)

    def list_tools(self):
        """Return registered tool names."""
        return list(self.tools.keys())

    def get_all(self):
        """Return all registered tools."""
        return list(self.tools.values())


from src.tools.calculator import add
from src.tools.user_profile import get_user_profile
from src.tools.memory_search import search_memory
from src.tools.date_time import get_current_time

from src.tools.jira import (
    get_jira_issues_assigned_to,
    get_open_inprogress_jira_issues,
    create_jira_issue,
)


registry = ToolRegistry()

registry.register(add)
registry.register(get_user_profile)
registry.register(search_memory)
registry.register(get_current_time)

registry.register(
    get_jira_issues_assigned_to
)

registry.register(
    get_open_inprogress_jira_issues
)

registry.register(
    create_jira_issue
)