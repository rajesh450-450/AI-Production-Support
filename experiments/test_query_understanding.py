from src.retrieval.query_understanding import QueryUnderstanding


def main() -> None:

    understanding = QueryUnderstanding()

    test_cases = [
        (
            "What is the root cause of KAN-1?",
            "jira-KAN-1",
        ),
        (
            "Please investigate jira-KAN-2 and tell me what happened.",
            "jira-KAN-2",
        ),
        (
            "Can you check jira-KAN-3?",
            "jira-KAN-3",
        ),
        (
            "Why are payment failures increasing?",
            None,
        ),
        (
            "Show me the latest production incidents.",
            None,
        ),
        (
            "",
            None,
        ),
    ]

    print("=" * 70)
    print("6.10.1 QUERY UNDERSTANDING TEST")
    print("=" * 70)
    print()

    passed = 0

    for query, expected_jira_id in test_cases:

        result = understanding.understand(query)

        print(f"Query    : {query}")
        print(f"result    : {result}")
        print(f"Detected : {result.jira_id}")
        print(f"Expected : {expected_jira_id}")
        print()

    print("=" * 70)
    print(f"RESULT: {passed}/{len(test_cases)} tests passed")
    print("=" * 70)



    print()
    print(" 6.10.1 QUERY UNDERSTANDING TEST COMPLETED")


if __name__ == "__main__":
    main()