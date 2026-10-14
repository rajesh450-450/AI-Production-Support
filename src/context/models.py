from dataclasses import dataclass, field


@dataclass
class ContextDocument:
    """
    Document prepared for LLM consumption.
    """

    text: str

    source: str

    metadata: dict = field(default_factory=dict)


@dataclass
class ContextBundle:
    """
    Final context passed to the LLM.
    """

    documents: list[ContextDocument]

    knowledge_context: str