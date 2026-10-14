from src.indexing.models import SourceDocument
from src.indexing.sources.base import KnowledgeSource


class IndexingSourcePipeline:
    """
    Loads knowledge from multiple sources and returns
    a common list of SourceDocument objects.

    The pipeline does not know how Confluence or Jira
    internally extract their data.
    """

    def __init__(
        self,
        sources: list[KnowledgeSource],
    ):
        self.sources = sources

    def load(self) -> list[SourceDocument]:
        """
        Load documents from all configured sources.
        """

        documents: list[SourceDocument] = []

        for source in self.sources:

            source_documents = source.load()

            documents.extend(source_documents)

        return documents