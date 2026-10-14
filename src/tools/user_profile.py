from langchain_core.tools import tool


@tool
def get_user_profile() -> str:
    """
    Returns the user's profile information.
    """

    return """
Name: Rajesh
Company: Mastercard
Role: Principal Data Engineer
Location: Hyderabad
"""