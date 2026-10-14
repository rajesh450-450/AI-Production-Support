from src.memory.conversation_memory import conversation_memory

from src.retrieval.bootstrap import create_retrieval_pipeline
from src.retrieval.models import RetrievalRequest

from src.utils.profiler import (
    start_profiler,
    stop_profiler,
)


# ---------------------------------------------------------
# Start Execution Trace
# ---------------------------------------------------------

start_profiler()

# ---------------------------------------------------------
# Prepare Conversation Memory
# ---------------------------------------------------------

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

conversation_memory.add(
    role="assistant",
    text="Use INFORMATION_SCHEMA to validate metadata.",
)

# ---------------------------------------------------------
# Build Retrieval Pipeline
# ---------------------------------------------------------

pipeline = create_retrieval_pipeline()

# ---------------------------------------------------------
# Query
# ---------------------------------------------------------

request = RetrievalRequest(
    query="restart",
    top_k=5,
)

response = pipeline.retrieve(request)

# ---------------------------------------------------------
# Print Results
# ---------------------------------------------------------

print("\n")
print("=" * 70)
print("Conversation Provider Results")
print("=" * 70)

for i, document in enumerate(response.documents, start=1):

    print(f"\nDocument #{i}")
    print(f"Provider : {document.source}")
    print(f"Score    : {document.score}")
    print(f"Content  : {document.text}")
    print(f"Metadata : {document.metadata}")

print("\n")
print("=" * 70)
print(f"Total Documents Retrieved : {len(response.documents)}")
print("=" * 70)

# ---------------------------------------------------------
# Stop Execution Trace
# ---------------------------------------------------------

stop_profiler()