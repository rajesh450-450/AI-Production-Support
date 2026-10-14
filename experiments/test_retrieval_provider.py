from src.retrieval.models import RetrievalRequest
from src.retrieval.providers.dummy_provider import DummyProvider


def main():

    print("=" * 60)
    print("Testing Retrieval Provider")
    print("=" * 60)

    provider = DummyProvider()

    request = RetrievalRequest(
        query="Why did Oracle validation fail?"
    )

    response = provider.retrieve(request)

    print(f"\nProvider : {provider.provider_name}")

    print(f"Documents Retrieved : {len(response.documents)}")

    for doc in response.documents:
        print("\nDocument")
        print(f"  ID      : {doc.id}")
        print(f"  Source  : {doc.source}")
        print(f"  Score   : {doc.score}")
        print(f"  Text    : {doc.text}")

    print("\n" + "=" * 60)
    print("Retrieval Provider Test Passed")
    print("=" * 60)


if __name__ == "__main__":
    main()