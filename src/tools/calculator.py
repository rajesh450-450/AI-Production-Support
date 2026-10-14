from langchain_core.tools import tool

@tool
def add(a: int, b: int) -> int:
    """
    Adds two integers.
    """
    return a + b