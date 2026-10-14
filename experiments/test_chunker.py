"""
6.6 - Chunker Validation

Validates the DocumentChunker implementation.
"""

from src.indexing.sources.confluence import ConfluenceSource
from src.indexing.sources.jira import JiraSource
from src.indexing.chunker import DocumentChunker


CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150
MIN_CHUNK_SIZE = 50


def calculate_overlap(previous_text: str, current_text: str) -> int:
    """
    Calculate the actual character overlap between two chunks.
    """

    max_overlap = min(
        len(previous_text),
        len(current_text),
    )

    for size in range(max_overlap, 0, -1):

        if previous_text[-size:] == current_text[:size]:
            return size

    return 0


def main():

    print("\n# CHUNKER TEST")

    print(f"\nChunk size    : {CHUNK_SIZE}")
    print(f"Chunk overlap : {CHUNK_OVERLAP}")

    # ============================================================
    # 1. LOAD SOURCE DOCUMENTS
    # ============================================================

    print("\nLoading Confluence...")

    confluence = ConfluenceSource()

    confluence_documents = confluence.load()

    print(
        f"Confluence documents loaded : "
        f"{len(confluence_documents)}"
    )

    print("\nLoading Jira...")

    jira = JiraSource()

    jira_documents = jira.load()

    print(
        f"Jira documents loaded : "
        f"{len(jira_documents)}"
    )

    documents = (
        confluence_documents
        + jira_documents
    )

    print(
        f"\nTotal documents : "
        f"{len(documents)}"
    )

    # ============================================================
    # 2. CREATE CHUNKS
    # ============================================================

    print("\nCreating chunks...")

    chunker = DocumentChunker(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    chunks = chunker.chunk_documents(
        documents
    )

    print(
        f"Total chunks : "
        f"{len(chunks)}"
    )

    # ============================================================
    # 3. MAXIMUM CHUNK SIZE
    # ============================================================

    oversized = [
        chunk
        for chunk in chunks
        if len(chunk.text) > CHUNK_SIZE
    ]

    if not oversized:

        print(
            f"\nPASS: All chunks are <= "
            f"{CHUNK_SIZE} characters."
        )

    else:

        print(
            f"\nFAIL: {len(oversized)} chunks "
            f"exceed {CHUNK_SIZE} characters."
        )

    # ============================================================
    # 4. VALID PARENT DOCUMENTS
    # ============================================================

    document_ids = {
        document.document_id
        for document in documents
    }

    invalid_parents = [
        chunk
        for chunk in chunks
        if chunk.document_id
        not in document_ids
    ]

    if not invalid_parents:

        print(
            "PASS: All chunks reference valid "
            "parent documents."
        )

    else:

        print(
            f"FAIL: {len(invalid_parents)} chunks "
            f"reference invalid documents."
        )

    # ============================================================
    # 5. CHUNK ID FORMAT
    # ============================================================

    invalid_ids = []

    for chunk in chunks:

        expected_prefix = (
            f"{chunk.document_id}-chunk-"
        )

        if not chunk.chunk_id.startswith(
            expected_prefix
        ):

            invalid_ids.append(chunk)

    if not invalid_ids:

        print(
            "PASS: All chunk IDs follow "
            "the expected format."
        )

    else:

        print(
            f"FAIL: {len(invalid_ids)} invalid "
            f"chunk IDs."
        )

    # ============================================================
    # 6. SEQUENTIAL CHUNK INDEXES
    # ============================================================

    chunks_by_document = {}

    for chunk in chunks:

        chunks_by_document.setdefault(
            chunk.document_id,
            [],
        ).append(chunk)

    invalid_sequences = []

    for document_id, document_chunks in (
        chunks_by_document.items()
    ):

        document_chunks.sort(
            key=lambda chunk: chunk.chunk_index
        )

        indexes = [
            chunk.chunk_index
            for chunk in document_chunks
        ]

        expected = list(
            range(len(indexes))
        )

        if indexes != expected:

            invalid_sequences.append(
                (
                    document_id,
                    indexes,
                )
            )

    if not invalid_sequences:

        print(
            "PASS: Chunk indexes are sequential "
            "for every document."
        )

    else:

        print(
            f"FAIL: {len(invalid_sequences)} "
            f"documents have invalid chunk indexes."
        )

    # ============================================================
    # 7. EMPTY CHUNKS
    # ============================================================

    empty_chunks = [
        chunk
        for chunk in chunks
        if not chunk.text.strip()
    ]

    if not empty_chunks:

        print(
            "PASS: No empty chunks were created."
        )

    else:

        print(
            f"FAIL: {len(empty_chunks)} "
            f"empty chunks found."
        )

    # ============================================================
    # 8. MINIMUM CHUNK SIZE
    # ============================================================

    small_chunks = [
        chunk
        for chunk in chunks
        if len(chunk.text) < MIN_CHUNK_SIZE
    ]

    if not small_chunks:

        print(
            f"PASS: No chunks are smaller than "
            f"{MIN_CHUNK_SIZE} characters."
        )

    else:

        print(
            f"FAIL: {len(small_chunks)} chunks "
            f"are smaller than {MIN_CHUNK_SIZE} "
            f"characters."
        )

    # ============================================================
    # 9. DUPLICATE CHUNKS
    # ============================================================

    seen = set()
    duplicate_chunks = []

    for chunk in chunks:

        key = (
            chunk.document_id,
            chunk.chunk_index,
            chunk.text,
        )

        if key in seen:

            duplicate_chunks.append(chunk)

        seen.add(key)

    if not duplicate_chunks:

        print(
            "PASS: No duplicate chunks were created."
        )

    else:

        print(
            f"FAIL: {len(duplicate_chunks)} "
            f"duplicate chunks found."
        )

    # ============================================================
    # 10. OVERLAP VALIDATION
    # ============================================================

    overlap_results = []

    for document_id, document_chunks in (
        chunks_by_document.items()
    ):

        document_chunks.sort(
            key=lambda chunk: chunk.chunk_index
        )

        for previous, current in zip(
            document_chunks,
            document_chunks[1:],
        ):

            actual_overlap = calculate_overlap(
                previous.text,
                current.text,
            )

            overlap_results.append(
                (
                    document_id,
                    previous.chunk_index,
                    current.chunk_index,
                    actual_overlap,
                )
            )

    incorrect_overlap = [
        result
        for result in overlap_results
        if result[3] != CHUNK_OVERLAP
    ]

    if not incorrect_overlap:

        print(
            "PASS: Consecutive chunks have "
            "the expected overlap."
        )

        if overlap_results:

            values = [
                result[3]
                for result in overlap_results
            ]

            print(
                f"Expected overlap : "
                f"{CHUNK_OVERLAP}"
            )

            print(
                f"Minimum actual   : "
                f"{min(values)}"
            )

            print(
                f"Maximum actual   : "
                f"{max(values)}"
            )

            print(
                f"Average actual   : "
                f"{sum(values) / len(values):.1f}"
            )

    else:

        print(
            f"FAIL: {len(incorrect_overlap)} "
            f"chunk pairs have incorrect overlap."
        )

        for result in incorrect_overlap[:10]:

            (
                document_id,
                previous_index,
                current_index,
                actual,
            ) = result

            print(
                f"  {document_id}: "
                f"{previous_index} -> "
                f"{current_index} "
                f"actual={actual}, "
                f"expected={CHUNK_OVERLAP}"
            )

    # ============================================================
    # 11. SAMPLE CHUNKS
    # ============================================================

    print("\n--- SAMPLE CHUNKS ---")

    for chunk in chunks[:5]:

        print(
            f"\nChunk ID     : "
            f"{chunk.chunk_id}"
        )

        print(
            f"Chunk index  : "
            f"{chunk.chunk_index}"
        )

        print(
            f"Text length  : "
            f"{len(chunk.text)}"
        )

        print("\nText:")
        print(chunk.text)

        if chunk.chunk_index > 0:

            previous = next(
                item
                for item in chunks_by_document[
                    chunk.document_id
                ]
                if item.chunk_index
                == chunk.chunk_index - 1
            )

            actual_overlap = calculate_overlap(
                previous.text,
                chunk.text,
            )

            print(
                f"\nActual overlap with previous: "
                f"{actual_overlap}"
            )

            print(
                "\nPrevious ending:"
            )

            print(
                repr(
                    previous.text[
                        -CHUNK_OVERLAP:
                    ]
                )
            )

            print(
                "\nCurrent beginning:"
            )

            print(
                repr(
                    chunk.text[
                        :CHUNK_OVERLAP
                    ]
                )
            )


if __name__ == "__main__":
    main()