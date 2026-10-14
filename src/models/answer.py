from typing import Literal

from pydantic import BaseModel


class FinalAnswer(BaseModel):
    """
    Final response returned to the user.
    """

    answer: str

    confidence: Literal[
        "low",
        "medium",
        "high",
    ]