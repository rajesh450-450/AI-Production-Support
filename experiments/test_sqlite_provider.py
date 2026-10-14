from src.memory.sqlite_memory import sqlite_memory

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
# Prepare Test Data
# ---------------------------------------------------------

sqlite_memory.clear()

sqlite_memory.add(
    text="Oracle validation failed because schema changed.",
    metadata={
        "source": "Runbook",
        "severity": "High",
    },
)

sqlite_memory.add(
    text="Restarting the NiFi processor resolves this issue.",
    metadata={
        "source": "Incident",
        "severity": "Medium",
    },
)

sqlite_memory.add(
    text="Databricks cluster restart clears stale executors.",
    metadata={
        "source": "Knowledge Base",
        "severity": "Low",
    },
)

# ---------------------------------------------------------
# Build Retrieval Pipeline
# ---------------------------------------------------------

pipeline = create_retrieval_pipeline()

# ---------------------------------------------------------
# Query
# ---------------------------------------------------------

request = RetrievalRequest(
    query="Oracle validation",
    top_k=5,
)

response = pipeline.retrieve(request)

# ---------------------------------------------------------
# Results
# ---------------------------------------------------------

print("\n")
print("=" * 60)
print("SQLite Provider Results")
print("=" * 60)

for document in response.documents:

    print(f"\nProvider : {document.source}")
    print(f"ID       : {document.id}")
    print(f"Score    : {document.score}")
    print(f"Content  : {document.text}")
    print(f"Metadata : {document.metadata}")

print("\n")
print("=" * 60)
print("Total Documents:", len(response.documents))
print("=" * 60)

# ---------------------------------------------------------
# Stop Execution Trace
# ---------------------------------------------------------

stop_profiler()