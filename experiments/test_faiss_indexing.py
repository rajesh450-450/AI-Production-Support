import json
from pathlib import Path

from src.indexing.chunk_store import ChunkStore
from src.indexing.faiss_index import FaissIndex


DB_PATH = "data/knowledge.db"
FAISS_PATH = "data/knowledge.faiss"
MAPPING_PATH = "data/faiss_chunk_ids.json"


def main() -> None:
    print("=" * 70)
    print("6.9 FAISS INDEXING CONTRACT TEST")
    print("=" * 70)

    chunk_store = ChunkStore(
        db_path=DB_PATH
    )

    faiss_index = FaissIndex(
        index_path=FAISS_PATH,
        mapping_path=MAPPING_PATH,
    )

    try:
        # ---------------------------------------------------------
        # 1. SQLite chunk count
        # ---------------------------------------------------------

        sqlite_count = chunk_store.size()

        print()
        print(f"SQLite chunks : {sqlite_count}")

        if sqlite_count == 0:
            raise AssertionError(
                "SQLite contains no chunks."
            )

        print("PASS: SQLite contains chunks.")

        # ---------------------------------------------------------
        # 2. FAISS vector count
        # ---------------------------------------------------------

        faiss_count = faiss_index.size()

        print(f"FAISS vectors : {faiss_count}")

        if faiss_count != sqlite_count:
            raise AssertionError(
                "FAISS vector count does not match "
                "SQLite chunk count."
            )

        print(
            "PASS: SQLite chunk count == "
            "FAISS vector count."
        )

        # ---------------------------------------------------------
        # 3. Mapping count
        # ---------------------------------------------------------

        with open(
            MAPPING_PATH,
            "r",
            encoding="utf-8",
        ) as file:
            chunk_ids = json.load(file)

        mapping_count = len(chunk_ids)

        print(f"Mapping entries : {mapping_count}")

        if mapping_count != faiss_count:
            raise AssertionError(
                "FAISS vector count does not match "
                "mapping count."
            )

        print(
            "PASS: FAISS vector count == "
            "mapping count."
        )

        # ---------------------------------------------------------
        # 4. No duplicate chunk IDs
        # ---------------------------------------------------------

        if len(chunk_ids) != len(set(chunk_ids)):
            raise AssertionError(
                "Duplicate chunk_id values found "
                "in FAISS mapping."
            )

        print(
            "PASS: No duplicate chunk IDs "
            "in FAISS mapping."
        )

        # ---------------------------------------------------------
        # 5. Every mapped chunk exists in SQLite
        # ---------------------------------------------------------

        for chunk_id in chunk_ids:

            chunk = chunk_store.get_by_id(
                chunk_id
            )

            if chunk is None:
                raise AssertionError(
                    "FAISS mapping references a "
                    f"chunk_id not found in SQLite: "
                    f"{chunk_id}"
                )

        print(
            "PASS: Every FAISS chunk_id "
            "exists in SQLite."
        )

        # ---------------------------------------------------------
        # 6. Verify vector position -> chunk_id
        # ---------------------------------------------------------

        sample_count = min(
            5,
            faiss_count,
        )

        print()
        print(
            f"Checking first {sample_count} "
            "FAISS vector mappings..."
        )

        for vector_index in range(
            sample_count
        ):

            chunk_id = faiss_index.get_chunk_id(
                vector_index
            )

            chunk = chunk_store.get_by_id(
                chunk_id
            )

            if chunk is None:
                raise AssertionError(
                    f"Vector {vector_index} maps "
                    f"to invalid chunk_id: {chunk_id}"
                )

            print(
                f"PASS: vector {vector_index} "
                f"-> {chunk_id}"
            )

        # ---------------------------------------------------------
        # 7. Validate FAISS internal consistency
        # ---------------------------------------------------------

        faiss_index.validate()

        print(
            "PASS: FAISS vector/mapping "
            "consistency validated."
        )

        # ---------------------------------------------------------
        # 8. Reload FAISS from disk
        # ---------------------------------------------------------

        reloaded_index = FaissIndex(
            index_path=FAISS_PATH,
            mapping_path=MAPPING_PATH,
        )

        if reloaded_index.size() != sqlite_count:
            raise AssertionError(
                "Reloaded FAISS vector count "
                "does not match SQLite."
            )

        if len(reloaded_index.chunk_ids) != sqlite_count:
            raise AssertionError(
                "Reloaded FAISS mapping count "
                "does not match SQLite."
            )

        print(
            "PASS: FAISS index and mapping "
            "reload successfully."
        )

        # ---------------------------------------------------------
        # 9. Verify reloaded mapping
        # ---------------------------------------------------------

        for vector_index in range(
            sample_count
        ):

            original_id = faiss_index.get_chunk_id(
                vector_index
            )

            reloaded_id = reloaded_index.get_chunk_id(
                vector_index
            )

            if original_id != reloaded_id:
                raise AssertionError(
                    "FAISS mapping changed after "
                    f"reload at vector {vector_index}."
                )

        print(
            "PASS: Vector -> chunk_id mapping "
            "survives reload."
        )

        # ---------------------------------------------------------
        # Final result
        # ---------------------------------------------------------

        print()
        print("=" * 70)
        print("PASS: 6.9 FAISS INDEXING CONTRACT TEST COMPLETED")
        print("=" * 70)

    finally:
        chunk_store.close()


if __name__ == "__main__":
    main()
