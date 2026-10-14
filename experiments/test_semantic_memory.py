from src.memory.semantic_memory import SemanticMemory

memory = SemanticMemory(
    dimension=768
)

print("Dimension :", memory.dimension)

print("Vectors   :", memory.size())