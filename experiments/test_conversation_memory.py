from src.memory.conversation_memory import conversation_memory

conversation_memory.clear()

conversation_memory.add(
    role="user",
    text="How do I restart a Databricks cluster?",
)

conversation_memory.add(
    role="assistant",
    text="Restart the cluster from the Compute page.",
)

conversation_memory.add(
    role="user",
    text="How do I validate an Oracle schema?",
)

print("\nRecent Messages")
print("-" * 50)

for doc in conversation_memory.recent():

    print(doc)

print("\nSearch Results")
print("-" * 50)

for doc in conversation_memory.search("restart"):

    print(doc)