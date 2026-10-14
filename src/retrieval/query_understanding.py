import re
from dataclasses import dataclass


@dataclass(frozen=True)
class QueryUnderstandingResult:
    """
    Result of query understanding.

    Contains:
        - original user query
        - normalized Jira document ID, if a Jira issue
          reference is detected
    """

    query: str
    jira_id: str | None = None


class QueryUnderstanding:
    """
    Understand the basic structure of a user query.

    Current responsibility:
        - Detect Jira issue IDs
        - Normalize Jira issue IDs to the internal
          document ID format used by the knowledge index

    Examples:

        PROJ-123
            -> jira-PROJ-123

        jira-PROJ-123
            -> jira-PROJ-123

        DATA-456
            -> jira-DATA-456

    This class does NOT perform:

        - SQLite lookup
        - FAISS search
        - Ranking
        - Retrieval
    """

    # ---------------------------------------------------------
    # Jira issue key
    #
    # Supported:
    #
    #   PROJ-123
    #   DATA-456
    #   ABC-1
    #
    # Optional "jira-" prefix is also supported:
    #
    #   jira-PROJ-123
    #   JIRA-PROJ-123
    #
    # Case-insensitive matching is intentional because
    # users may type Jira references in different cases.
    # ---------------------------------------------------------

    JIRA_ID_PATTERN = re.compile(
        r"\b(?:jira-)?([A-Z][A-Z0-9]+-\d+)\b",
        re.IGNORECASE,
    )

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def understand(
        self,
        query: str,
    ) -> QueryUnderstandingResult:
        """
        Analyze a user query and detect a Jira issue ID.

        The returned Jira ID is always normalized to:

            jira-<ISSUE_KEY>

        Example:

            "What is PROJ-123 status?"
                -> "jira-PROJ-123"
        """

        if not query:
            return QueryUnderstandingResult(
                query=query,
                jira_id=None,
            )

        match = self.JIRA_ID_PATTERN.search(
            query
        )

        if match is None:
            return QueryUnderstandingResult(
                query=query,
                jira_id=None,
            )

        issue_key = match.group(1).upper()

        normalized_jira_id = (
            f"jira-{issue_key}"
        )

        return QueryUnderstandingResult(
            query=query,
            jira_id=normalized_jira_id,
        )