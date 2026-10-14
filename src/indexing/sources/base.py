from abc import ABC, abstractmethod

from src.indexing.models import SourceDocument


class KnowledgeSource(ABC):
    """
    Common interface for external knowledge sources.

    Examples:
        - Confluence
        - Jira
    """

    @property
    @abstractmethod
    def source_name(self) -> str:
        """
        Return the name of the knowledge source.
        """
        pass

    @abstractmethod
    def load(self) -> list[SourceDocument]:
        """
        Load documents from the source.

        Returns:
            A list of normalized SourceDocument objects.
        """
        pass