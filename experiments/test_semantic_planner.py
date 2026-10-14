from src.memory.semantic_memory import semantic_memory

# Clear memory for a clean test
semantic_memory.documents.clear()
semantic_memory.index.reset()

# Add knowledge
semantic_memory.add("I work at Mastercard.")
semantic_memory.add("I am a Principal Data Engineer.")
semantic_memory.add("I know Databricks.")
semantic_memory.add("I live in Hyderabad.")

print("Semantic memory initialized.")
print("Total memories:", semantic_memory.size())