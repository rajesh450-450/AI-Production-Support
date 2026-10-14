from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RetrievedDocument:
    """
    A single piece of knowledge returned by a retrieval provider.

    This model is provider-agnostic and should not expose
    implementation details of FAISS, SQLite, or any other source.
    """

    id: str

    text: str

    source: str

    score: float = 0.0

    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RetrievalRequest:
    """
    Request submitted to the retrieval pipeline.
    """

    query: str

    top_k: int = 5

    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RetrievalResponse:
    """
    Response returned by the retrieval pipeline.
    """

    documents: list[RetrievedDocument] = field(default_factory=list)