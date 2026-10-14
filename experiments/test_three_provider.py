from src.memory.semantic_memory import semantic_memory
from src.memory.sqlite_memory import sqlite_memory
from src.memory.conversation_memory import conversation_memory

from src.retrieval.bootstrap import create_retrieval_pipeline
from src.retrieval.models import RetrievalRequest

from src.utils.profiler import (
    start_profiler,
    stop_profiler,
)

# ---------------------------------------------------------
# Start Profiler
# ---------------------------------------------------------

start_profiler()

# ---------------------------------------------------------
# Reset Memory Stores
# ---------------------------------------------------------

semantic_memory.clear()
sqlite_memory.clear()
conversation_memory.clear()

# ---------------------------------------------------------
# Populate FAISS
# ---------------------------------------------------------

semantic_memory.add(
    text="Restart the Databricks cluster if executors become unhealthy.",
    metadata={
        "category": "Databricks",
    },
)

semantic_memory.add(
    text="Spark adaptive query execution improves joins.",
    metadata={
        "category": "Spark",
    },
)

# ---------------------------------------------------------
# Populate SQLite
# ---------------------------------------------------------

sqlite_memory.add(
    text="Restarting the NiFi processor resolves scheduler issues.",
    metadata={
        "category": "NiFi",
    },
)

sqlite_memory.add(
    text="Oracle schema validation should be performed before deployment.",
    metadata={
        "category": "Oracle",
    },
)

# ---------------------------------------------------------
# Populate Conversation Memory
# ---------------------------------------------------------

conversation_memory.add(
    role="user",
    text="How do I restart a Databricks cluster?",
)

conversation_memory.add(
    role="assistant",
    text="Use the Compute page to restart the cluster.",
)

# ---------------------------------------------------------
# Build Pipeline
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
# Results
# ---------------------------------------------------------

print("\n")
print("=" * 70)
print("Three Provider Retrieval Results")
print("=" * 70)

provider_counts = {}

for i, document in enumerate(response.documents, start=1):

    provider_counts[document.source] = (
        provider_counts.get(document.source, 0) + 1
    )

    print(f"\nDocument #{i}")
    print(f"Provider : {document.source}")
    print(f"Score    : {document.score}")
    print(f"Content  : {document.text}")
    print(f"Metadata : {document.metadata}")

print("\n")
print("=" * 70)
print("Provider Summary")
print("=" * 70)

for provider, count in provider_counts.items():
    print(f"{provider:<15} : {count}")

print("\n")
print("=" * 70)
print(f"Total Documents : {len(response.documents)}")
print("=" * 70)

# ---------------------------------------------------------
# Stop Profiler
# ---------------------------------------------------------

stop_profiler()