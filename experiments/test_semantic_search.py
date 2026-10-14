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

results = memory.search(
    "Where do I work?"
)

print()

print("Search Results")

for result in results:
    print(result)