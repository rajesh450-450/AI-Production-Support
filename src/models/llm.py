from src.config.settings import settings
from langchain_google_genai import ChatGoogleGenerativeAI

from src.models.schemas import (
    InvestigationPlan,
    ReviewDecision,
    FinalAnswer,
)
from src.tools.registry import registry

llm = ChatGoogleGenerativeAI(
    model=settings.model_name,
    google_api_key=settings.google_api_key,
    temperature=0,
)
planner_llm = llm.with_structured_output(
    InvestigationPlan
)

reviewer_llm = llm.with_structured_output(
    ReviewDecision
)

executor_llm = llm.bind_tools(
    registry.get_all()
)

answer_llm = llm.with_structured_output(
    FinalAnswer
)