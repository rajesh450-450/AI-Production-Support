from src.memory.execution_context import execution_context


execution_context.reset()

execution_context.update_metadata(
    question="Where do I work?",
    user="Rajesh",
)

execution_context.update_current(
    current_agent="Planner",
    current_step=1,
)

execution_context.publish(
    "planner",
    "Plan created successfully.",
)

print(execution_context.get())