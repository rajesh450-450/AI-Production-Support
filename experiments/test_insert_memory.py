from src.memory.conversation_memory import ConversationMemory

memory = ConversationMemory()

# Optional:
# memory.clear()

# memory.add_user_message(
#     "What is 50 + 70?"
# )

# memory.add_assistant_message(
#     "The answer is 120."
# )

# memory.add_user_message(
#     "Multiply the result by 5."
# )

# memory.add_assistant_message(
#     "120 × 5 = 600."
# )

# memory.add_user_message(
#     "Who created Apache Spark?"
# )

# memory.add_assistant_message(
#     "Apache Spark was originally created by Matei Zaharia at UC Berkeley."
# )
memory.clear()
print("Conversation inserted successfully.")