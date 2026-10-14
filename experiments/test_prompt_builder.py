from src.context.models import AgentContext
from src.prompts.builder import PromptBuilder


def main():

    context = AgentContext(
        question="What is 5 + 70?",
        retrieved_documents=[
            "Calculator tool is available."
        ],
    )

    builder = PromptBuilder()

    prompt = builder.build_planner(context)

    print("\n=========== Planner Prompt ===========\n")
    print(prompt)
    print("\n======================================\n")


if __name__ == "__main__":
    main()