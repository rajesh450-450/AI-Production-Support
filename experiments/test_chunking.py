import sys
import re

sys.stdout.reconfigure(encoding="utf-8")

from src.indexing.pipeline import IndexingSourcePipeline

from src.indexing.sources.confluence import (
    ConfluenceSource,
)

from src.indexing.sources.jira import (
    JiraSource,
)

from src.indexing.chunker import (
    DocumentChunker,
)


# ============================================================================
# CONFIGURATION
# ============================================================================

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


# ============================================================================
# HELPERS
# ============================================================================

def print_header(title: str) -> None:

    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def normalize_for_comparison(text: str) -> str:
    """
    Normalize text only for overlap comparison.

    This is NOT used by the chunker.

    It prevents insignificant whitespace differences from causing
    false overlap failures during validation.
    """

    return re.sub(
        r"\s+",
        " ",
        text,
    ).strip()


def calculate_actual_overlap(
    previous_text: str,
    current_text: str,
) -> int:
    """
    Calculate the longest suffix of previous_text that appears
    as the prefix of current_text.

    Example:

        previous:
        "...executor memory pressure and Spark partitioning"

        current:
        "executor memory pressure and Spark partitioning..."

        overlap = length of the common boundary text
    """

    previous = normalize_for_comparison(
        previous_text
    )

    current = normalize_for_comparison(
        current_text
    )

    max_possible = min(
        len(previous),
        len(current),
    )

    for length in range(
        max_possible,
        0,
        -1,
    ):

        if previous[-length:] == current[:length]:
            return length

    return 0


# ============================================================================
# VALIDATION 1
# ============================================================================

def validate_max_chunk_size(
    chunks,
    chunk_size: int,
) -> None:

    print_header(
        "VALIDATION 1 - MAXIMUM CHUNK SIZE"
    )

    invalid = [
        chunk
        for chunk in chunks
        if len(chunk.text) > chunk_size
    ]

    if invalid:

        print(
            "\nERROR: Chunks exceed maximum size:"
        )

        for chunk in invalid[:20]:

            print(
                f"  {chunk.chunk_id} "
                f"| length={len(chunk.text)}"
            )

        raise RuntimeError(
            "Maximum chunk size validation failed."
        )

    print(
        f"\nPASS: All chunks are <= "
        f"{chunk_size} characters."
    )


# ============================================================================
# VALIDATION 2
# ============================================================================

def validate_document_mapping(
    documents,
    chunks,
) -> None:

    print_header(
        "VALIDATION 2 - DOCUMENT -> CHUNK MAPPING"
    )

    document_ids = {
        document.document_id
        for document in documents
    }

    invalid = [
        chunk
        for chunk in chunks
        if chunk.document_id not in document_ids
    ]

    if invalid:

        print(
            "\nERROR: Chunks reference unknown "
            "documents:"
        )

        for chunk in invalid[:20]:

            print(
                f"  {chunk.chunk_id} "
                f"-> {chunk.document_id}"
            )

        raise RuntimeError(
            "Document-to-chunk mapping validation failed."
        )

    print(
        "\nPASS: All chunks reference valid "
        "parent documents."
    )


# ============================================================================
# VALIDATION 3
# ============================================================================

def validate_chunk_ids(
    chunks,
) -> None:

    print_header(
        "VALIDATION 3 - CHUNK ID CONSISTENCY"
    )

    pattern = re.compile(
        r"^.+-chunk-\d{4}$"
    )

    invalid = [
        chunk
        for chunk in chunks
        if not pattern.match(chunk.chunk_id)
    ]

    if invalid:

        print(
            "\nERROR: Invalid chunk IDs:"
        )

        for chunk in invalid[:20]:

            print(
                f"  {chunk.chunk_id}"
            )

        raise RuntimeError(
            "Chunk ID validation failed."
        )

    print(
        "\nPASS: All chunk IDs follow "
        "the expected format."
    )


# ============================================================================
# VALIDATION 4
# ============================================================================

def validate_chunk_indexes(
    chunks,
) -> None:

    print_header(
        "VALIDATION 4 - CHUNK INDEX SEQUENCING"
    )

    chunks_by_document = {}

    for chunk in chunks:

        chunks_by_document.setdefault(
            chunk.document_id,
            [],
        ).append(chunk)

    errors = []

    for document_id, document_chunks in (
        chunks_by_document.items()
    ):

        document_chunks.sort(
            key=lambda chunk: chunk.chunk_index
        )

        expected_index = 0

        for chunk in document_chunks:

            if chunk.chunk_index != expected_index:

                errors.append(
                    (
                        document_id,
                        chunk.chunk_index,
                        expected_index,
                    )
                )

            expected_index += 1

    if errors:

        print(
            "\nERROR: Chunk indexes are not sequential:"
        )

        for (
            document_id,
            actual,
            expected,
        ) in errors[:20]:

            print(
                f"  {document_id} "
                f"| expected={expected} "
                f"| actual={actual}"
            )

        raise RuntimeError(
            "Chunk index sequencing validation failed."
        )

    print(
        "\nPASS: Chunk indexes are sequential "
        "for every document."
    )


# ============================================================================
# VALIDATION 5
# ============================================================================

def validate_overlap(
    chunks,
    target_overlap: int,
) -> None:

    print_header(
        "VALIDATION 5 - CHUNK OVERLAP"
    )

    chunks_by_document = {}

    for chunk in chunks:

        chunks_by_document.setdefault(
            chunk.document_id,
            [],
        ).append(chunk)

    overlap_results = []

    failures = []

    for document_id, document_chunks in (
        chunks_by_document.items()
    ):

        document_chunks.sort(
            key=lambda chunk: chunk.chunk_index
        )

        if len(document_chunks) <= 1:
            continue

        for previous, current in zip(
            document_chunks,
            document_chunks[1:],
        ):

            actual_overlap = calculate_actual_overlap(
                previous.text,
                current.text,
            )

            overlap_results.append(
                (
                    document_id,
                    previous,
                    current,
                    actual_overlap,
                )
            )

            if actual_overlap == 0:

                failures.append(
                    (
                        document_id,
                        previous,
                        current,
                    )
                )

    if failures:

        print(
            "\nERROR: Some consecutive chunks "
            "have no overlap:"
        )

        for (
            document_id,
            previous,
            current,
        ) in failures[:20]:

            print(
                f"\n  Document : {document_id}"
            )

            print(
                f"  Previous : "
                f"{previous.chunk_index:04d}"
            )

            print(
                f"  Current  : "
                f"{current.chunk_index:04d}"
            )

            print(
                f"  Previous length : "
                f"{len(previous.text)}"
            )

            print(
                f"  Current length  : "
                f"{len(current.text)}"
            )

            print(
                "\n  Previous ending:"
            )

            print(
                repr(
                    previous.text[-250:]
                )
            )

            print(
                "\n  Current beginning:"
            )

            print(
                repr(
                    current.text[:250]
                )
            )

        raise RuntimeError(
            "Chunk overlap validation failed."
        )

    if not overlap_results:

        print(
            "\nPASS: No multi-chunk documents "
            "required overlap validation."
        )

        return

    overlaps = [
        actual
        for (
            _,
            _,
            _,
            actual,
        ) in overlap_results
    ]

    minimum = min(overlaps)
    maximum = max(overlaps)
    average = sum(overlaps) / len(overlaps)

    print(
        "\nPASS: All consecutive multi-chunk "
        "documents contain overlap."
    )

    print(
        f"Target overlap : "
        f"{target_overlap} characters"
    )

    print(
        f"Minimum actual : "
        f"{minimum} characters"
    )

    print(
        f"Maximum actual : "
        f"{maximum} characters"
    )

    print(
        f"Average actual : "
        f"{average:.1f} characters"
    )

    print(
        "\nOverlap distribution:"
    )

    print(
        f"  < 50 chars     : "
        f"{sum(x < 50 for x in overlaps)}"
    )

    print(
        f"  50-99 chars    : "
        f"{sum(50 <= x < 100 for x in overlaps)}"
    )

    print(
        f"  100-124 chars  : "
        f"{sum(100 <= x < 125 for x in overlaps)}"
    )

    print(
        f"  125-149 chars  : "
        f"{sum(125 <= x < 150 for x in overlaps)}"
    )

    print(
        f"  >= 150 chars   : "
        f"{sum(x >= 150 for x in overlaps)}"
    )


# ============================================================================
# VALIDATION 6
# ============================================================================

def validate_no_empty_chunks(
    chunks,
) -> None:

    print_header(
        "VALIDATION 6 - EMPTY CHUNKS"
    )

    invalid = [
        chunk
        for chunk in chunks
        if not chunk.text.strip()
    ]

    if invalid:

        print(
            "\nERROR: Empty chunks detected:"
        )

        for chunk in invalid[:20]:

            print(
                f"  {chunk.chunk_id}"
            )

        raise RuntimeError(
            "Empty chunk validation failed."
        )

    print(
        "\nPASS: No empty chunks were created."
    )


# ============================================================================
# VALIDATION 7
# ============================================================================

def validate_duplicate_chunks(
    chunks,
) -> None:

    print_header(
        "VALIDATION 7 - DUPLICATE CHUNKS"
    )

    seen = set()
    duplicates = []

    for chunk in chunks:

        key = (
            chunk.document_id,
            chunk.chunk_index,
            chunk.text,
        )

        if key in seen:

            duplicates.append(
                chunk.chunk_id
            )

        seen.add(key)

    if duplicates:

        print(
            "\nERROR: Duplicate chunks detected:"
        )

        for chunk_id in duplicates[:20]:

            print(
                f"  {chunk_id}"
            )

        raise RuntimeError(
            "Duplicate chunk validation failed."
        )

    print(
        "\nPASS: No duplicate chunks were created."
    )


# ============================================================================
# SAMPLE OUTPUT
# ============================================================================

def print_sample_chunks(
    chunks,
    number_of_chunks: int = 10,
) -> None:

    print_header(
        f"SAMPLE CHUNKS - FIRST {number_of_chunks}"
    )

    for chunk in chunks[:number_of_chunks]:

        print("\n" + "-" * 80)

        print(
            f"Chunk ID     : {chunk.chunk_id}"
        )

        print(
            f"Document ID  : {chunk.document_id}"
        )

        print(
            f"Source       : {chunk.source}"
        )

        print(
            f"Title        : {chunk.title}"
        )

        print(
            f"Chunk index  : {chunk.chunk_index}"
        )

        print(
            f"Text length  : {len(chunk.text)}"
        )

        print("\nText:")

        print(chunk.text[:500])


# ============================================================================
# OVERLAP SAMPLE
# ============================================================================

def print_overlap_samples(
    chunks,
    number_of_samples: int = 5,
) -> None:

    print_header(
        f"OVERLAP INSPECTION - {number_of_samples} SAMPLES"
    )

    samples_printed = 0

    chunks_by_document = {}

    for chunk in chunks:

        chunks_by_document.setdefault(
            chunk.document_id,
            [],
        ).append(chunk)

    for document_id, document_chunks in (
        chunks_by_document.items()
    ):

        document_chunks.sort(
            key=lambda chunk: chunk.chunk_index
        )

        if len(document_chunks) < 2:
            continue

        for previous, current in zip(
            document_chunks,
            document_chunks[1:],
        ):

            overlap = calculate_actual_overlap(
                previous.text,
                current.text,
            )

            print("\n" + "-" * 80)

            print(
                f"Document : {document_id}"
            )

            print(
                f"Chunks   : "
                f"{previous.chunk_index:04d} "
                f"-> "
                f"{current.chunk_index:04d}"
            )

            print(
                f"Actual overlap : "
                f"{overlap} characters"
            )

            print(
                "\nPrevious chunk ending:"
            )

            print(
                repr(
                    previous.text[-200:]
                )
            )

            print(
                "\nCurrent chunk beginning:"
            )

            print(
                repr(
                    current.text[:200]
                )
            )

            samples_printed += 1

            if samples_printed >= number_of_samples:
                return


# ============================================================================
# SUMMARY
# ============================================================================

def print_summary(
    documents,
    chunks,
) -> None:

    print_header(
        "6.6 DOCUMENT CHUNKING SUMMARY"
    )

    print(
        f"\nDocuments loaded : {len(documents)}"
    )

    print(
        f"Chunks created   : {len(chunks)}"
    )

    source_counts = {}

    for chunk in chunks:

        source_counts.setdefault(
            chunk.source,
            0,
        )

        source_counts[chunk.source] += 1

    print("\nChunks by source:")

    for source, count in sorted(
        source_counts.items()
    ):

        print(
            f"  {source:<15} : {count}"
        )


# ============================================================================
# MAIN TEST
# ============================================================================

def run_test():

    print_header(
        "6.6 DOCUMENT CHUNKING"
    )

    print(
        "\nChunk configuration:"
    )

    print(
        f"  Maximum chunk size : "
        f"{CHUNK_SIZE}"
    )

    print(
        f"  Target overlap     : "
        f"{CHUNK_OVERLAP}"
    )

    # ------------------------------------------------------------------------
    # Load sources
    # ------------------------------------------------------------------------

    print(
        "\nLoading source documents..."
    )

    confluence = ConfluenceSource()

    jira = JiraSource()

    source_pipeline = IndexingSourcePipeline(
        sources=[
            confluence,
            jira,
        ]
    )

    documents = source_pipeline.load()

    # ------------------------------------------------------------------------
    # Create chunker
    # ------------------------------------------------------------------------

    chunker = DocumentChunker(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    # ------------------------------------------------------------------------
    # Create chunks
    # ------------------------------------------------------------------------

    chunks = chunker.chunk_documents(
        documents
    )

    print_summary(
        documents,
        chunks,
    )

    # ------------------------------------------------------------------------
    # Validations
    # ------------------------------------------------------------------------

    validate_max_chunk_size(
        chunks,
        CHUNK_SIZE,
    )

    validate_document_mapping(
        documents,
        chunks,
    )

    validate_chunk_ids(
        chunks,
    )

    validate_chunk_indexes(
        chunks,
    )

    validate_overlap(
        chunks,
        CHUNK_OVERLAP,
    )

    validate_no_empty_chunks(
        chunks,
    )

    validate_duplicate_chunks(
        chunks,
    )

    # ------------------------------------------------------------------------
    # Samples
    # ------------------------------------------------------------------------

    print_sample_chunks(
        chunks,
        number_of_chunks=10,
    )

    print_overlap_samples(
        chunks,
        number_of_samples=5,
    )

    # ------------------------------------------------------------------------
    # Final result
    # ------------------------------------------------------------------------

    print_header(
        "6.6 FINAL RESULT"
    )

    print(
        "\nPASS: Document chunking validation completed."
    )

    print(
        "\nValidated:"
    )

    print(
        "  [PASS] Maximum chunk size"
    )

    print(
        "  [PASS] Document -> chunk mapping"
    )

    print(
        "  [PASS] Chunk ID consistency"
    )

    print(
        "  [PASS] Chunk index sequencing"
    )

    print(
        "  [PASS] Chunk overlap"
    )

    print(
        "  [PASS] No empty chunks"
    )

    print(
        "  [PASS] No duplicate chunks"
    )

    print(
        "\n6.6 TEST COMPLETED"
    )


if __name__ == "__main__":
    run_test()