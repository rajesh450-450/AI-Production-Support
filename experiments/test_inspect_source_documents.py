import sys

sys.stdout.reconfigure(
    encoding="utf-8"
)

from src.indexing.pipeline import IndexingSourcePipeline
from src.indexing.sources.confluence import ConfluenceSource
from src.indexing.sources.jira import JiraSource


def run_test():

    confluence = ConfluenceSource()
    jira = JiraSource()

    pipeline = IndexingSourcePipeline(
        sources=[
            confluence,
            jira,
        ]
    )

    documents = pipeline.load()

    print("=" * 80)
    print("SOURCE DOCUMENT INSPECTION")
    print("=" * 80)

    # --------------------------------------------------
    # One Confluence document
    # --------------------------------------------------

    confluence_doc = next(
        document
        for document in documents
        if document.source == "confluence"
    )

    print("\n" + "=" * 80)
    print("CONFLUENCE DOCUMENT")
    print("=" * 80)

    print(f"Document ID : {confluence_doc.document_id}")
    print(f"Title       : {confluence_doc.title}")
    print(f"Text length : {len(confluence_doc.text)}")

    print("\n--- TEXT ---")
    print(confluence_doc.text)

    print("\n--- REPR ---")
    print(repr(confluence_doc.text))

    # --------------------------------------------------
    # One Jira document
    # --------------------------------------------------

    jira_doc = next(
        document
        for document in documents
        if document.source == "jira"
    )

    print("\n" + "=" * 80)
    print("JIRA DOCUMENT")
    print("=" * 80)

    print(f"Document ID : {jira_doc.document_id}")
    print(f"Title       : {jira_doc.title}")
    print(f"Text length : {len(jira_doc.text)}")

    print("\n--- TEXT ---")
    print(jira_doc.text)

    print("\n--- REPR ---")
    print(repr(jira_doc.text))

    print("\n" + "=" * 80)
    print("INSPECTION COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    run_test()