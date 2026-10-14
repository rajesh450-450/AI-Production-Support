from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class MemoryDocument:
    """
    Document stored inside SemanticMemory.

    This is an internal infrastructure model and is not exposed
    outside the memory subsystem.
    """

    id: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)