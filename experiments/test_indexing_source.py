from src.indexing.models import SourceDocument
from src.indexing.sources.base import KnowledgeSource


class TestSource(KnowledgeSource):

    @property
    def source_name(self) -> str:
        return "test"

    def load(self) -> list[SourceDocument]:
        return [
            SourceDocument(
                document_id="test-001",
                source="test",
                external_id="001",
                title="Test Document",
                text="This is a test document.",
            )
        ]


def run_test():
    source = TestSource()

    documents = source.load()

    assert source.source_name == "test"
    assert len(documents) == 1
    assert documents[0].document_id == "test-001"
    assert documents[0].text == "This is a test document."

    print("6.2 Source Interface test passed.")


if __name__ == "__main__":
    run_test()