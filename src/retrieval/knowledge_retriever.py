from src.indexing.chunk_store import ChunkStore
from src.indexing.faiss_index import FaissIndex

from src.retrieval.models import (
    RetrievalRequest,
    RetrievalResponse,
    RetrievedDocument,
)

from src.retrieval.query_understanding import (
    QueryUnderstanding,
)

from src.retrieval.ranking.knowledge_ranking import (
    KnowledgeRankingStrategy,
)

from src.retrieval.ranking.pipeline import (
    RankingPipeline,
)


class KnowledgeRetriever:
    """
    Retrieves knowledge using exact Jira lookup
    and semantic FAISS search.

    Responsibilities:
        - Understand the query
        - Perform exact Jira lookup when Jira ID exists
        - Perform semantic FAISS search
        - Resolve FAISS chunk IDs from SQLite
        - Build a candidate set
        - Remove duplicate candidates
        - Rank candidates
        - Apply top_k
    """

    def __init__(
        self,
        chunk_store: ChunkStore,
        query_understanding: QueryUnderstanding,
        faiss_index: FaissIndex,
    ) -> None:

        self.chunk_store = chunk_store
        self.query_understanding = query_understanding
        self.faiss_index = faiss_index

        self.ranking_pipeline = (
            RankingPipeline()
            .add_strategy(
                KnowledgeRankingStrategy()
            )
        )

    def retrieve(
        self,
        request: RetrievalRequest,
    ) -> RetrievalResponse:
        """
        Build, rank, and return the final candidate set.
        """

        understanding = (
            self.query_understanding.understand(
                request.query
            )
        )

        candidates: list[RetrievedDocument] = []

        # ====================================================
        # EXACT JIRA CANDIDATES
        # ====================================================

        if understanding.jira_id is not None:

            jira_candidates = (
                self._retrieve_jira(
                    understanding.jira_id
                )
            )

            candidates.extend(
                jira_candidates
            )

        # ====================================================
        # SEMANTIC CANDIDATES
        # ====================================================

        semantic_candidates = (
            self._retrieve_semantic(
                request
            )
        )

        candidates.extend(
            semantic_candidates
        )

        # ====================================================
        # DEDUPLICATION
        # ====================================================

        candidates = self._deduplicate(
            candidates
        )

        # ====================================================
        # RANKING
        # ====================================================

        ranked_candidates = (
            self.ranking_pipeline.rank(
                candidates
            )
        )

        # ====================================================
        # TOP K
        # ====================================================

        ranked_candidates = ranked_candidates[
            :request.top_k
        ]

        return RetrievalResponse(
            documents=ranked_candidates
        )

    # ========================================================
    # SEMANTIC RETRIEVAL
    # ========================================================

    def _retrieve_semantic(
        self,
        request: RetrievalRequest,
    ) -> list[RetrievedDocument]:
        """
        Retrieve candidates using FAISS.

        SQLite remains the authoritative source
        for chunk information.
        """

        faiss_results = self.faiss_index.search(
            query=request.query,
            top_k=request.top_k,
        )

        documents: list[RetrievedDocument] = []

        for result in faiss_results:

            chunk_id = result["chunk_id"]

            score = float(
                result["score"]
            )

            chunk = self.chunk_store.get_by_id(
                chunk_id
            )

            if chunk is None:
                continue

            metadata = dict(
                chunk.metadata
            )

            metadata[
                "retrieval_type"
            ] = "semantic"

            documents.append(
                RetrievedDocument(
                    id=chunk.chunk_id,
                    text=chunk.text,
                    source=chunk.source,
                    score=score,
                    metadata=metadata,
                )
            )

        return documents

    # ========================================================
    # EXACT JIRA RETRIEVAL
    # ========================================================

    def _retrieve_jira(
        self,
        jira_id: str,
    ) -> list[RetrievedDocument]:
        """
        Retrieve all chunks belonging to a Jira issue.

        SQLite is the authoritative source.
        """

        document_id = jira_id

        chunks = (
            self.chunk_store.get_by_document_id(
                document_id
            )
        )

        documents: list[RetrievedDocument] = []

        for chunk in chunks:

            metadata = dict(
                chunk.metadata
            )

            metadata[
                "retrieval_type"
            ] = "exact"

            documents.append(
                RetrievedDocument(
                    id=chunk.chunk_id,
                    text=chunk.text,
                    source=chunk.source,
                    score=1.0,
                    metadata=metadata,
                )
            )

        return documents

    # ========================================================
    # DEDUPLICATION
    # ========================================================

    @staticmethod
    def _deduplicate(
        documents: list[RetrievedDocument],
    ) -> list[RetrievedDocument]:
        """
        Remove duplicate candidates using chunk_id.

        The first occurrence is retained.
        """

        seen: set[str] = set()

        unique_documents: list[
            RetrievedDocument
        ] = []

        for document in documents:

            if document.id in seen:
                continue

            seen.add(document.id)

            unique_documents.append(
                document
            )

        return unique_documents