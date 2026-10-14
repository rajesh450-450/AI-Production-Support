from src.memory.working_memory import working_memory

working_memory.set(
    "question",
    "Why did the pipeline fail?"
)

working_memory.set(
    "current_step",
    2
)

working_memory.set(
    "status",
    "Running"
)

print(working_memory.get_all())
print(
    working_memory.get("question")
)

print(
    working_memory.get("status")
)