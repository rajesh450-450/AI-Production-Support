from src.retrieval.models import RetrievedDocument
from src.retrieval.ranking.knowledge_ranking import (
    KnowledgeRankingStrategy,
)


def main() -> None:

    print()
    print("=" * 70)
    print("6.10.5 RANKING CONTRACT TEST")
    print("=" * 70)

    strategy = KnowledgeRankingStrategy()

    # ========================================================
    # TEST 1: EXACT JIRA CANDIDATES COME FIRST
    # ========================================================

    print()
    print("TEST 1: Exact Jira candidates have highest priority")
    print("-" * 70)

    documents = [
        RetrievedDocument(
            id="semantic-1",
            text="Semantic result 1",
            source="confluence",
            score=0.20,
            metadata={
                "retrieval_type": "semantic"
            },
        ),
        RetrievedDocument(
            id="jira-1",
            text="Exact Jira result 1",
            source="jira",
            score=1.0,
            metadata={
                "retrieval_type": "exact"
            },
        ),
        RetrievedDocument(
            id="semantic-2",
            text="Semantic result 2",
            source="jira",
            score=0.10,
            metadata={
                "retrieval_type": "semantic"
            },
        ),
        RetrievedDocument(
            id="jira-2",
            text="Exact Jira result 2",
            source="jira",
            score=1.0,
            metadata={
                "retrieval_type": "exact"
            },
        ),
    ]

    ranked = strategy.rank(documents)
    print("ranked output")
    print(ranked)

    for index, document in enumerate(
        ranked,
        start=1,
    ):
        print(
            f"{index}. "
            f"{document.id} | "
            f"{document.metadata['retrieval_type']} | "
            f"score={document.score}"
        )

    expected_order = [
        "jira-1",
        "jira-2",
        "semantic-2",
        "semantic-1",
    ]

    actual_order = [
        document.id
        for document in ranked
    ]

    if actual_order != expected_order:
        print()
        print("FAIL: Ranking order is incorrect.")
        return

    print()
    print(
        "PASS: Exact Jira candidates are ranked first."
    )

    # ========================================================
    # TEST 2: SEMANTIC CANDIDATES USE LOWEST FAISS DISTANCE
    # ========================================================

    print()
    print(
        "TEST 2: Semantic candidates ordered by FAISS distance"
    )
    print("-" * 70)

    semantic_documents = [
        RetrievedDocument(
            id="semantic-3",
            text="Semantic result 3",
            source="confluence",
            score=0.80,
            metadata={
                "retrieval_type": "semantic"
            },
        ),
        RetrievedDocument(
            id="semantic-4",
            text="Semantic result 4",
            source="confluence",
            score=0.30,
            metadata={
                "retrieval_type": "semantic"
            },
        ),
        RetrievedDocument(
            id="semantic-5",
            text="Semantic result 5",
            source="confluence",
            score=0.60,
            metadata={
                "retrieval_type": "semantic"
            },
        ),
    ]

    ranked = strategy.rank(
        semantic_documents
    )

    for index, document in enumerate(
        ranked,
        start=1,
    ):
        print(
            f"{index}. "
            f"{document.id} | "
            f"distance={document.score}"
        )

    expected_order = [
        "semantic-4",
        "semantic-5",
        "semantic-3",
    ]

    actual_order = [
        document.id
        for document in ranked
    ]

    if actual_order != expected_order:
        print()
        print(
            "FAIL: Semantic ranking order is incorrect."
        )
        return

    print()
    print(
        "PASS: Semantic candidates are ordered "
        "by lowest FAISS distance."
    )

    # ========================================================
    # TEST 3: JIRA SOURCE DOES NOT AUTOMATICALLY MEAN EXACT
    # ========================================================

    print()
    print(
        "TEST 3: FAISS Jira result remains semantic"
    )
    print("-" * 70)

    documents = [
        RetrievedDocument(
            id="jira-semantic",
            text="Jira document found by FAISS",
            source="jira",
            score=0.20,
            metadata={
                "retrieval_type": "semantic"
            },
        ),
        RetrievedDocument(
            id="jira-exact",
            text="Jira document found by exact lookup",
            source="jira",
            score=1.0,
            metadata={
                "retrieval_type": "exact"
            },
        ),
    ]

    ranked = strategy.rank(documents)

    for index, document in enumerate(
        ranked,
        start=1,
    ):
        print(
            f"{index}. "
            f"{document.id} | "
            f"{document.metadata['retrieval_type']} | "
            f"score={document.score}"
        )

    if ranked[0].id != "jira-exact":
        print()
        print(
            "FAIL: Exact Jira result was not ranked first."
        )
        return

    if ranked[1].id != "jira-semantic":
        print()
        print(
            "FAIL: Semantic Jira result was incorrectly "
            "treated as exact."
        )
        return

    print()
    print(
        "PASS: Retrieval type is used correctly."
    )

    # ========================================================
    # FINAL RESULT
    # ========================================================

    print()
    print("=" * 70)
    print(
        "PASS: 6.10.5 RANKING CONTRACT TEST COMPLETED"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()