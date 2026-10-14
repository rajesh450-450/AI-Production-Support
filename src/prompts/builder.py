from src.context.models import ContextBundle
from src.models.schemas import PlanStep

from src.prompts.planner import PLANNER_PROMPT
from src.prompts.executor import EXECUTOR_PROMPT

from src.tools.registry import registry


class PromptBuilder:
    """
    Builds prompts for AI agents.

    Responsibilities
    ----------------
    - Own prompt templates
    - Convert ContextBundle into LLM prompts
    - Build dynamic tool catalogs
    - Keep prompt formatting out of agents

    This class NEVER:
    - Performs retrieval
    - Calls the LLM
    - Updates workflow state
    """

    # ---------------------------------------------------------
    # Tool Catalog
    # ---------------------------------------------------------

    @staticmethod
    def build_tool_catalog() -> str:
        """
        Build the Planner's available-tool catalog directly
        from the ToolRegistry.

        This avoids maintaining a separate hard-coded list
        inside the Planner prompt.
        """

        tools = registry.get_all()

        if not tools:
            return "No external tools are currently available."

        lines = []

        for tool in tools:
            description = getattr(
                tool,
                "description",
                "No description available.",
            )

            lines.append(
                f"- {tool.name}\n"
                f"  {description}"
            )

        return "\n".join(lines)

    # ---------------------------------------------------------
    # Planner
    # ---------------------------------------------------------

    def build_planner(
        self,
        question: str,
        context: ContextBundle,
        evidence: list,
        plan_history: list,
        review_history: list,
        planning_iteration: int,
    ) -> str:

        tool_catalog = self.build_tool_catalog()

        return f"""
{PLANNER_PROMPT}

==================================================
PLANNING ITERATION
==================================================

{planning_iteration}

==================================================
AVAILABLE TOOLS
==================================================

{tool_catalog}

==================================================
AVAILABLE CONTEXT
==================================================

{context.knowledge_context}

==================================================
PREVIOUS PLANS
==================================================

{plan_history}

==================================================
PREVIOUS EVIDENCE
==================================================

{evidence}

==================================================
PREVIOUS REVIEW DECISIONS
==================================================

{review_history}

==================================================
USER QUESTION
==================================================

{question}
"""

    # ---------------------------------------------------------
    # Executor
    # ---------------------------------------------------------

    def build_executor(
        self,
        question: str,
        context: ContextBundle,
        step: PlanStep,
        evidence: list,
    ) -> str:

        return f"""
{EXECUTOR_PROMPT}

==================================================
AVAILABLE CONTEXT
==================================================

{context.knowledge_context}

==================================================
USER QUESTION
==================================================

{question}

==================================================
CURRENT STEP
==================================================

Step Number:
{step.step}

Step Type:
{step.type}

Description:
{step.description}

Expected Tool:
{step.tool if step.tool else "None"}

==================================================
PREVIOUS EVIDENCE
==================================================

{evidence}
"""