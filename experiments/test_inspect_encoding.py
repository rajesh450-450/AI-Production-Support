import sys

from src.indexing.sources.confluence import ConfluenceSource
from src.indexing.sources.jira import JiraSource


def inspect_document(document):
    print("\n" + "=" * 80)
    print("DOCUMENT")
    print("=" * 80)

    print(f"Document ID : {document.document_id}")
    print(f"Source      : {document.source}")
    print(f"Title       : {document.title}")
    print(f"Text length : {len(document.text)}")

    print("\n--- SPECIAL CHARACTERS ---")

    found = False

    for index, char in enumerate(document.text):
        code = ord(char)

        # Print characters outside normal ASCII.
        if code > 127:
            found = True

            print(
                f"Position {index:5} | "
                f"Character {repr(char):10} | "
                f"Unicode U+{code:04X}"
            )

    if not found:
        print("No non-ASCII characters found.")

    print("\n--- FIRST 1000 CHARACTERS ---")
    print(document.text[:1000])

    print("\n--- repr() ---")
    print(repr(document.text[:1000]))


def main():
    print("=" * 80)
    print("ENCODING DIAGNOSTIC")
    print("=" * 80)

    # --------------------------------------------------
    # Confluence
    # --------------------------------------------------

    print("\nLoading Confluence...")

    confluence = ConfluenceSource()

    documents = confluence.load()

    print(f"Confluence documents loaded : {len(documents)}")

    if not documents:
        raise RuntimeError(
            "No Confluence documents were loaded."
        )

    # Inspect first Confluence document.
    inspect_document(documents[0])

    # --------------------------------------------------
    # Jira
    # --------------------------------------------------

    print("\n" + "=" * 80)
    print("JIRA")
    print("=" * 80)

    print("\nLoading Jira...")

    jira = JiraSource()

    jira_documents = jira.load()

    print(f"Jira documents loaded : {len(jira_documents)}")

    if not jira_documents:
        raise RuntimeError(
            "No Jira documents were loaded."
        )

    # Inspect first Jira document.
    inspect_document(jira_documents[0])

    print("\n" + "=" * 80)
    print("ENCODING DIAGNOSTIC COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    main()