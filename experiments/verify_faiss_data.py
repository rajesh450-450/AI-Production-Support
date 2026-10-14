import json
import sqlite3
from pathlib import Path

import faiss
import sys

sys.stdout.reconfigure(encoding="utf-8")

FAISS_PATH = Path("data/knowledge.faiss")
MAPPING_PATH = Path("data/faiss_chunk_ids.json")
SQLITE_PATH = Path("data/knowledge.db")


def main() -> None:
    print("=" * 70)
    print("FAISS DATA VERIFICATION")
    print("=" * 70)

    # ---------------------------------------------------------
    # Check files
    # ---------------------------------------------------------

    if not FAISS_PATH.exists():
        raise FileNotFoundError(
            f"FAISS index not found: {FAISS_PATH}"
        )

    if not MAPPING_PATH.exists():
        raise FileNotFoundError(
            f"FAISS mapping not found: {MAPPING_PATH}"
        )

    if not SQLITE_PATH.exists():
        raise FileNotFoundError(
            f"SQLite database not found: {SQLITE_PATH}"
        )

    # ---------------------------------------------------------
    # Load FAISS
    # ---------------------------------------------------------

    index = faiss.read_index(
        str(FAISS_PATH)
    )

    with open(
        MAPPING_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        chunk_ids = json.load(file)

    print()
    print("FAISS")
    print("-" * 70)
    print(f"Dimension       : {index.d}")
    print(f"Vector count    : {index.ntotal}")
    print(f"Mapping count   : {len(chunk_ids)}")

    # ---------------------------------------------------------
    # Basic FAISS validation
    # ---------------------------------------------------------

    if index.ntotal != len(chunk_ids):
        raise AssertionError(
            "FAISS vector count does not match "
            "chunk_id mapping count."
        )

    if len(chunk_ids) != len(set(chunk_ids)):
        raise AssertionError(
            "Duplicate chunk_ids found in FAISS mapping."
        )

    print("PASS: Vector count == mapping count.")
    print("PASS: All FAISS chunk_ids are unique.")

    # ---------------------------------------------------------
    # Load SQLite
    # ---------------------------------------------------------

    connection = sqlite3.connect(
        SQLITE_PATH
    )

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            chunk_id,
            document_id,
            source,
            external_id,
            title,
            text,
            chunk_index
        FROM chunks
        ORDER BY chunk_id
        """
    )

    rows = cursor.fetchall()

    sqlite_chunk_ids = {
        row["chunk_id"]
        for row in rows
    }

    print()
    print("SQLITE")
    print("-" * 70)
    print(f"Chunk count     : {len(rows)}")

    # ---------------------------------------------------------
    # Compare SQLite and FAISS
    # ---------------------------------------------------------

    faiss_chunk_ids = set(chunk_ids)

    if faiss_chunk_ids != sqlite_chunk_ids:

        missing_from_faiss = (
            sqlite_chunk_ids - faiss_chunk_ids
        )

        extra_in_faiss = (
            faiss_chunk_ids - sqlite_chunk_ids
        )

        print()
        print("FAIL: SQLite and FAISS chunk IDs differ.")

        if missing_from_faiss:
            print()
            print("Missing from FAISS:")
            for chunk_id in sorted(
                missing_from_faiss
            ):
                print(f"  {chunk_id}")

        if extra_in_faiss:
            print()
            print("Extra in FAISS:")
            for chunk_id in sorted(
                extra_in_faiss
            ):
                print(f"  {chunk_id}")

        raise AssertionError(
            "SQLite chunk IDs != FAISS chunk IDs."
        )

    print(
        "PASS: SQLite chunk IDs == FAISS chunk IDs."
    )

    # ---------------------------------------------------------
    # Display sample vector mappings
    # ---------------------------------------------------------

    print()
    print("SAMPLE VECTOR → CHUNK MAPPINGS")
    print("-" * 70)

    sample_count = min(
        10,
        index.ntotal,
    )

    rows_by_id = {
        row["chunk_id"]: row
        for row in rows
    }

    for vector_index in range(
        sample_count
    ):

        chunk_id = chunk_ids[
            vector_index
        ]

        row = rows_by_id[
            chunk_id
        ]

        print()
        print(
            f"Vector index : {vector_index}"
        )
        print(
            f"Chunk ID     : {chunk_id}"
        )
        print(
            f"Document ID  : {row['document_id']}"
        )
        print(
            f"Source       : {row['source']}"
        )
        print(
            f"Title        : {row['title']}"
        )
        print(
            f"Chunk index  : {row['chunk_index']}"
        )
        print(
            f"Text length  : {len(row['text'])}"
        )
        print(
            f"Text preview : "
            f"{row['text'][:150].replace(chr(10), ' ')}"
        )

    # ---------------------------------------------------------
    # Read sample vector
    # ---------------------------------------------------------

    if index.ntotal > 0:

        vector = index.reconstruct(0)

        print()
        print("SAMPLE VECTOR")
        print("-" * 70)
        print(
            f"Vector index : 0"
        )
        print(
            f"Chunk ID     : {chunk_ids[0]}"
        )
        print(
            f"Dimensions   : {len(vector)}"
        )
        print(
            "First 10 values:"
        )

        for value in vector[:10]:
            print(
                f"  {value:.6f}"
            )

    connection.close()

    print()
    print("=" * 70)
    print("PASS: FAISS DATA VERIFICATION COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()