from src.indexing.sources.jira import JiraSource


def main():

    source = JiraSource()

    documents = source.load()

    print()
    print("=" * 80)
    print("JIRA SOURCE TEST")
    print("=" * 80)

    print()
    print(f"Source       : {source.source_name}")
    print(f"Project      : {source.project_key}")
    print(f"Documents    : {len(documents)}")

    for document in documents:

        print()
        print("-" * 80)

        print(
            f"Document ID  : {document.document_id}"
        )

        print(
            f"External ID  : {document.external_id}"
        )

        print(
            f"Title        : {document.title}"
        )

        print(
            f"Source       : {document.source}"
        )

        print(
            f"Created      : {document.created_at}"
        )

        print(
            f"Updated      : {document.updated_at}"
        )

        print()
        print("Content:")
        print(
            document.text[:1000]
        )


if __name__ == "__main__":
    main()