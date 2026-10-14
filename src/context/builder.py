from collections import defaultdict

from src.context.models import (
    ContextBundle,
    ContextDocument,
)

from src.retrieval.models import (
    RetrievalResponse,
)


class ContextBuilder:
    """
    Converts RetrievalResponse into an LLM-ready ContextBundle.
    """

    # ---------------------------------------------------------
    # Preferred Provider Order
    #
    # New providers can be added later without changing
    # the rest of the builder.
    # ---------------------------------------------------------

    SECTION_ORDER = [
        "conversation",
        "faiss",
        "sqlite",
    ]

    # ---------------------------------------------------------
    # Public
    # ---------------------------------------------------------

    def build(
        self,
        retrieval_response: RetrievalResponse,
    ) -> ContextBundle:

        grouped_documents = defaultdict(list)

        context_documents = []

        # -----------------------------------------------------
        # Convert RetrievedDocument -> ContextDocument
        # -----------------------------------------------------

        for retrieved_document in retrieval_response.documents:

            context_document = ContextDocument(
                text=retrieved_document.text,
                source=retrieved_document.source,
                metadata=retrieved_document.metadata,
            )

            context_documents.append(
                context_document
            )

            grouped_documents[
                retrieved_document.source.lower()
            ].append(
                context_document
            )

        prompt = self._build_prompt(
            grouped_documents
        )

        return ContextBundle(
            documents=context_documents,
            knowledge_context=prompt,
        )

    # ---------------------------------------------------------
    # Private
    # ---------------------------------------------------------

    def _build_prompt(
        self,
        grouped_documents,
    ) -> str:

        sections = []

        # -----------------------------------------------------
        # Conversation
        # -----------------------------------------------------

        self._append_section(
            sections=sections,
            title="Conversation",
            documents=grouped_documents.get(
                "conversation",
                [],
            ),
        )

        # -----------------------------------------------------
        # Knowledge
        # -----------------------------------------------------

        knowledge_documents = []

        # Preferred provider order

        for provider in self.SECTION_ORDER:

            if provider == "conversation":
                continue

            knowledge_documents.extend(
                grouped_documents.get(
                    provider,
                    [],
                )
            )

        # Any future providers (Confluence, Jira, etc.)

        for provider, documents in grouped_documents.items():

            if provider in self.SECTION_ORDER:
                continue

            knowledge_documents.extend(
                documents
            )

        self._append_section(
            sections=sections,
            title="Knowledge",
            documents=knowledge_documents,
        )

        return "\n\n".join(sections)

    def _append_section(
        self,
        sections: list[str],
        title: str,
        documents: list[ContextDocument],
    ) -> None:
        """
        Adds a formatted section if documents exist.
        """

        if not documents:
            return

        sections.append(
            f"{title}\n{'=' * len(title)}"
        )

        for document in documents:

            sections.append(
                document.text
            )