from langchain_core.tools import tool

from src.memory.semantic_memory import semantic_memory


@tool
def search_memory(query: str) -> str:
    """
    Search semantic memory.
    """

    results = semantic_memory.search(query)

    if not results:
        return "No relevant memories found."

    return "\n".join(results)