class RetrievalPolicy:
    """
    Decides whether enterprise knowledge retrieval
    is required for a user query.

    Conversation retrieval is NOT controlled by this policy.
    Conversation retrieval always happens.

    This policy only controls:
        - Jira retrieval
        - FAISS / enterprise knowledge retrieval
    """

    def should_retrieve_knowledge(
        self,
        query: str,
    ) -> bool:
        """
        Return True when enterprise knowledge retrieval
        should be performed.

        Initial policy:
        - Explicit Jira issue reference -> YES
        - Incident / production-support question -> YES
        - General/simple questions -> NO
        """

        query_lower = query.lower().strip()

        if not query_lower:
            return False

        # -------------------------------------------------
        # Explicit Jira issue reference
        # -------------------------------------------------

        if self._contains_jira_reference(query):
            return True

        # -------------------------------------------------
        # Production / incident related queries
        # -------------------------------------------------

        knowledge_keywords = (
            "pipeline",
            "job",
            "failure",
            "failed",
            "error",
            "incident",
            "production",
            "prod",
            "issue",
            "root cause",
            "rca",
            "schema",
            "dataset",
            "data quality",
            "etl",
            "nifi",
            "databricks",
            "spark",
            "hadoop",
            "aws",
            "s3",
        )

        return any(
            keyword in query_lower
            for keyword in knowledge_keywords
        )

    # -----------------------------------------------------
    # Jira Detection
    # -----------------------------------------------------

    @staticmethod
    def _contains_jira_reference(
        query: str,
    ) -> bool:
        """
        Detect Jira-style issue keys.

        Examples:
            ABC-123
            PROJ-456
            DATA-1
            jira-ABC-123
        """

        import re

        pattern = re.compile(
            r"\b(?:jira-)?[A-Z][A-Z0-9]+-\d+\b",
            re.IGNORECASE,
        )

        return pattern.search(query) is not None