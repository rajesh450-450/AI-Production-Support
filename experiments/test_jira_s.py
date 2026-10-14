from src.services.jira_service import JiraService


def main():

    jira_service = JiraService()

    # =====================================================
    # TEST 1: RESOLVE RAJESH
    # =====================================================

    print("\n" + "=" * 70)
    print("TEST 1: RESOLVE JIRA USER - RAJESH")
    print("=" * 70)

    user = jira_service.resolve_user(
        "Rajesh"
    )

    if user is None:

        print("User not found.")

    else:

        print("User resolved successfully.")

        print(
            f"Display Name : "
            f"{user.get('displayName', '')}"
        )

        print(
            f"Account ID   : "
            f"{user.get('accountId', '')}"
        )

        print(
            f"Active       : "
            f"{user.get('active')}"
        )

        print("\nFull user object:")
        print(user)

    # =====================================================
    # TEST 2: ISSUES ASSIGNED TO RAJESH
    # =====================================================

    print("\n" + "=" * 70)
    print("TEST 2: ISSUES ASSIGNED TO RAJESH")
    print("=" * 70)

    try:

        issues = jira_service.get_issues_assigned_to(
            assignee="Rajesh"
        )

        print(
            f"Number of issues: {len(issues)}"
        )

        if not issues:

            print(
                "No open/in-progress issues "
                "were returned for Rajesh."
            )

        for issue in issues:

            fields = issue.get(
                "fields",
                {}
            )

            status = fields.get(
                "status"
            ) or {}

            priority = fields.get(
                "priority"
            ) or {}

            assignee = fields.get(
                "assignee"
            ) or {}

            print(
                "\n"
                f"Key      : {issue.get('key', '')}\n"
                f"Summary  : {fields.get('summary', '')}\n"
                f"Status   : {status.get('name', '')}\n"
                f"Assignee : {assignee.get('displayName', 'Unassigned')}\n"
                f"Priority : {priority.get('name', '')}"
            )

    except Exception as e:

        print(
            f"ERROR: {type(e).__name__}: {e}"
        )

    # =====================================================
    # TEST 3: ALL OPEN / IN-PROGRESS ISSUES
    # =====================================================

    print("\n" + "=" * 70)
    print("TEST 3: ALL OPEN / IN-PROGRESS ISSUES")
    print("=" * 70)

    try:

        issues = (
            jira_service
            .get_open_inprogress_issues()
        )

        print(
            f"Number of issues: {len(issues)}"
        )

        for issue in issues:

            fields = issue.get(
                "fields",
                {}
            )

            status = fields.get(
                "status"
            ) or {}

            priority = fields.get(
                "priority"
            ) or {}

            assignee = fields.get(
                "assignee"
            ) or {}

            print(
                "\n"
                f"Key      : {issue.get('key', '')}\n"
                f"Summary  : {fields.get('summary', '')}\n"
                f"Status   : {status.get('name', '')}\n"
                f"Assignee : {assignee.get('displayName', 'Unassigned')}\n"
                f"Priority : {priority.get('name', '')}"
            )

    except Exception as e:

        print(
            f"ERROR: {type(e).__name__}: {e}"
        )


if __name__ == "__main__":
    main()