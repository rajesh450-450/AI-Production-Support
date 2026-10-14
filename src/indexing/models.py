from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class SourceDocument:
    """
    Normalized document extracted from an external knowledge source.

    Examples:
        - Jira issue
        - Confluence page
    """

    document_id: str
    source: str
    external_id: str
    title: str
    text: str

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    content_hash: str = ""

    created_at: str | None = None
    updated_at: str | None = None


# @dataclass(slots=True)
# class DocumentChunk:
#     """
#     A chunk created from a SourceDocument.

#     Chunks are the units that will eventually be
#     embedded and indexed in FAISS.
#     """

#     chunk_id: str
#     document_id: str
#     text: str

#     metadata: dict[str, Any] = field(
#         default_factory=dict
#     )


@dataclass(slots=True)
class DocumentChunk:
    """
    A searchable chunk created from a SourceDocument.

    A chunk always retains its parent document identity.
    """

    chunk_id: str
    document_id: str

    source: str
    external_id: str

    title: str

    text: str

    chunk_index: int

    metadata: dict[str, Any] = field(
        default_factory=dict
    )