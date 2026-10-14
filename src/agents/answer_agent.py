from src.models.llm import answer_llm
from src.prompts.answer import ANSWER_PROMPT
from src.memory.execution_context import execution_context
from src.memory.conversation_memory import ConversationMemory
conversation_memory = ConversationMemory()

def answer_node(state):
    """
    Generate the final user-facing answer after the reviewer
    has approved the investigation.
    """
    print("\n" + "=" * 80)
    print("ENTERING ANSWER")
    print("=" * 80)
    execution_context.add_event(
        "INFO",
        "AnswerGenerator",
        "Answer generation started.",
    )

    prompt = f"""
{ANSWER_PROMPT}

Question:
{state["question"]}

Relevant Knowledge:
{state["context_bundle"].knowledge_context}

Plan:
{state["plan"]}

Evidence:
{state["evidence"]}

Review Status:
{state["review_status"]}

Review Reason:
{state["review_reason"]}
"""
    execution_context.update_progress(
        current_phase="Answer Generation",
        current_step=execution_context.get().progress.total_steps,
        current_tool="",
    )
    print("\n" + "=" * 70)
    print("ANSWER GENERATOR")
    print("=" * 70)
    print("\n----- ANSWER PROMPT -----")
    print(prompt)

    execution_context.increment_llm_calls()
    answer = answer_llm.invoke(prompt)

    print("\n----- FINAL ANSWER -----")
    print(answer)

    execution_context.add_event(
        "INFO",
        "AnswerGenerator",
        "Final answer generated.",
    )

    state["answer"] = answer

    # ---------------------------------------------------------
    # Store Conversation
    # ---------------------------------------------------------
    # ---------------------------------------------------------
    # Convert FinalAnswer to plain text for Conversation Memory
    # ---------------------------------------------------------

    if hasattr(answer, "answer"):
        answer_text = answer.answer
    else:
        answer_text = str(answer)

    # conversation_memory.add(
    #     conversation_id=state["conversation_id"],
    #     role="user",
    #     text=state["question"],
    # )

    # conversation_memory.add(
    #     conversation_id=state["conversation_id"],
    #     role="assistant",
    #     text=answer_text,
    # )



    print("\n----- CONVERSATION MEMORY -----")
    print(
        conversation_memory.recent(
            conversation_id=state["conversation_id"]
        )
    )

    print("\nLeaving Answer")
    execution_context.add_event(
        "INFO",
        "AnswerGenerator",
        "Answer generation completed.",
    )
    return state