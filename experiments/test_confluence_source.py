from src.indexing.sources.confluence import ConfluenceSource
import sys

sys.stdout.reconfigure(encoding="utf-8")

def run_test():

    source = ConfluenceSource()

    print("\n" + "=" * 70)
    print("CONFLUENCE SOURCE TEST")
    print("=" * 70)

    print(f"Source : {source.source_name}")
    print(f"Space  : {source.space_key}")

    documents = source.load()

    print(f"\nDocuments extracted: {len(documents)}")

    for document in documents:

        print("\n" + "-" * 60)

        print(f"Document ID : {document.document_id}")
        print(f"External ID : {document.external_id}")
        print(f"Title       : {document.title}")
        print(f"Source      : {document.source}")
        print(f"Created     : {document.created_at}")
        print(f"Updated     : {document.updated_at}")

        print("\nContent:")
        print(document.text[:500])

    print("\n" + "=" * 70)
    print("CONFLUENCE EXTRACTION SUCCESSFUL")
    print("=" * 70)


if __name__ == "__main__":
    run_test()