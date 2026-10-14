from src.indexing.pipeline import IndexingSourcePipeline

from src.indexing.sources.confluence import ConfluenceSource
from src.indexing.sources.jira import JiraSource
import sys

sys.stdout.reconfigure(encoding="utf-8")

def run_test():

    print("\n" + "=" * 80)
    print("6.5 SOURCE → COMMON DOCUMENTS")
    print("=" * 80)

    # --------------------------------------------------
    # Create sources
    # --------------------------------------------------

    confluence = ConfluenceSource()
    jira = JiraSource()

    # --------------------------------------------------
    # Create common indexing pipeline
    # --------------------------------------------------

    pipeline = IndexingSourcePipeline(
        sources=[
            confluence,
            jira,
        ]
    )

    # --------------------------------------------------
    # Load documents
    # --------------------------------------------------

    documents = pipeline.load()

    # --------------------------------------------------
    # Results
    # --------------------------------------------------

    print(f"\nTotal documents : {len(documents)}")

    print("\nDocuments by source:")

    source_counts = {}

    for document in documents:

        source_counts.setdefault(
            document.source,
            0,
        )

        source_counts[document.source] += 1

    for source, count in source_counts.items():

        print(
            f"  {source:<15} : {count}"
        )

    # --------------------------------------------------
    # Show sample documents
    # --------------------------------------------------

    print("\nSample documents:")

    for document in documents[:5]:

        print("\n" + "-" * 80)

        print(
            f"Document ID : {document.document_id}"
        )

        print(
            f"External ID : {document.external_id}"
        )

        print(
            f"Source      : {document.source}"
        )

        print(
            f"Title       : {document.title}"
        )

        print(
            f"Created     : {document.created_at}"
        )

        print(
            f"Updated     : {document.updated_at}"
        )

        print(
            f"Text length : {len(document.text)}"
        )

    print("\n" + "=" * 80)
    print("6.5 TEST COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    run_test()