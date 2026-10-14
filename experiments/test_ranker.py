from src.retrieval.models import RetrievedDocument


documents = [
    RetrievedDocument(
        id="1",
        text="Low Score",
        metadata={},
        source="faiss",
        score=0.20,
    ),
    RetrievedDocument(
        id="2",
        text="Highest Score",
        metadata={},
        source="sqlite",
        score=0.95,
    ),
    RetrievedDocument(
        id="3",
        text="Medium Score",
        metadata={},
        source="conversation",
        score=0.60,
    ),
]

ranker = RetrievalRanker()

ranked = ranker.rank(documents)

print("\nRanked Documents")
print("=" * 50)

for document in ranked:
    print(f"{document.score:.2f}  |  {document.source:<12} | {document.text}")