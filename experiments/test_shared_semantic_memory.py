from src.memory.semantic_memory import semantic_memory

semantic_memory.add(
    "I work at Mastercard."
)

print("Size after add:")
print(semantic_memory.size())

results = semantic_memory.search(
    "Where do I work?"
)

print("\nSearch Results:")

for result in results:
    print(result)