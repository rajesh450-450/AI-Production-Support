from src.utils.profiler import start_profiler, stop_profiler
from src.memory.semantic_memory import semantic_memory

from src.retrieval.bootstrap import create_retrieval_pipeline
from src.retrieval.models import RetrievalRequest
start_profiler()

semantic_memory.documents.clear()
semantic_memory.index.reset()

semantic_memory.add(
    "Oracle validation failed because the schema changed."
)

semantic_memory.add(
    "Customer table contains duplicate records."
)

pipeline = create_retrieval_pipeline()

response = pipeline.retrieve(
    RetrievalRequest(
        query="Why did Oracle validation fail?",
        top_k=2,
    )
)

print("\nRetrieved Documents\n")

for doc in response.documents:
    print(doc)

stop_profiler()