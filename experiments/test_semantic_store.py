from src.memory.semantic_memory import SemanticMemory

memory = SemanticMemory()

memory.add(
    "I work at Mastercard."
)

memory.add(
    "I live in Hyderabad."
)

memory.add(
    "I know Databricks."
)

print()

print("Stored Documents")

for doc in memory.documents:
    print(doc)

print()

print("FAISS Size")

print(memory.size())