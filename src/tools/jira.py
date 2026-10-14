from langchain_core.tools import tool

from src.services.jira_service import JiraService


jira_service = JiraService()


# =========================================================
# GET ISSUES ASSIGNED TO USER
# =========================================================

@tool
def get_jira_issues_assigned_to(
    assignee: str,
) -> str:
    """
    Get open Jira issues assigned to a specific user.
    """

    issues = (
        jira_service.get_issues_assigned_to(
            assignee=assignee,
        )
    )

    if not issues:
        return (
            f"No open Jira issues found "
            f"for {assignee}."
        )

    results = []

    for issue in issues:

        fields = issue.get(
            "fields",
            {},
        ) or {}

        status = fields.get(
            "status"
        ) or {}

        priority = fields.get(
            "priority"
        ) or {}

        results.append(
            "\n".join(
                [
                    f"Key: {issue.get('key', '')}",
                    f"Summary: {fields.get('summary', '')}",
                    f"Status: {status.get('name', '')}",
                    f"Priority: {priority.get('name', '')}",
                    (
                        f"URL: "
                        f"{jira_service.url}/browse/"
                        f"{issue.get('key', '')}"
                    ),
                ]
            )
        )

    return "\n\n".join(results)


# =========================================================
# GET OPEN / IN-PROGRESS ISSUES
# =========================================================

@tool
def get_open_inprogress_jira_issues() -> str:
    """
    Get all currently open or in-progress Jira issues.
    """

    issues = (
        jira_service.get_open_inprogress_issues()
    )

    if not issues:
        return (
            "No open or in-progress Jira issues found."
        )

    results = []

    for issue in issues:

        fields = issue.get(
            "fields",
            {},
        ) or {}

        status = fields.get(
            "status"
        ) or {}

        assignee = fields.get(
            "assignee"
        ) or {}

        priority = fields.get(
            "priority"
        ) or {}

        results.append(
            "\n".join(
                [
                    f"Key: {issue.get('key', '')}",
                    f"Summary: {fields.get('summary', '')}",
                    f"Status: {status.get('name', '')}",
                    (
                        f"Assignee: "
                        f"{assignee.get('displayName', 'Unassigned')}"
                    ),
                    f"Priority: {priority.get('name', '')}",
                ]
            )
        )

    return "\n\n".join(results)


# =========================================================
# CREATE JIRA ISSUE
# =========================================================

@tool
def create_jira_issue(
    summary: str,
    description: str,
    issue_type: str = "Task",
) -> str:
    """
    Create a new Jira issue.
    """

    issue = jira_service.create_issue(
        summary=summary,
        description=description,
        issue_type=issue_type,
    )

    issue_key = issue.get(
        "key",
        "",
    )

    issue_url = (
        f"{jira_service.url}/browse/{issue_key}"
    )

    return (
        f"Jira issue created successfully.\n"
        f"Key: {issue_key}\n"
        f"URL: {issue_url}"
    )

# =========================================================
# GET JIRA ISSUE BY KEY
# =========================================================

@tool
def get_jira_issue_by_key(
    issue_key: str,
) -> str:
    """
    Retrieve a specific Jira issue by its issue key.

    Example:
        KAN-12
        PROJ-123

    This performs a direct live lookup in Jira and returns
    the issue's key, summary, description, status, project,
    issue type, priority, and URL.
    """

    issue_key = issue_key.strip().upper()

    if not issue_key:
        return "Jira issue key cannot be empty."

    issues = jira_service.search_issues(
        jql=f'key = "{issue_key}"',
        limit=1,
    )

    if not issues:
        return (
            f"Jira issue '{issue_key}' was not found."
        )

    issue = issues[0]

    fields = issue.get(
        "fields",
        {},
    ) or {}

    project = fields.get(
        "project",
        {},
    ) or {}

    status = fields.get(
        "status",
        {},
    ) or {}

    issue_type = fields.get(
        "issuetype",
        {},
    ) or {}

    priority = fields.get(
        "priority",
        {},
    ) or {}

    description = fields.get(
        "description",
        "",
    )

    return "\n".join(
        [
            f"Key: {issue.get('key', issue_key)}",
            f"Summary: {fields.get('summary', '')}",
            f"Description: {description}",
            f"Status: {status.get('name', '')}",
            f"Project: {project.get('key', '')} - "
            f"{project.get('name', '')}",
            f"Issue Type: {issue_type.get('name', '')}",
            f"Priority: {priority.get('name', '')}",
            (
                f"URL: "
                f"{jira_service.url}/browse/"
                f"{issue.get('key', issue_key)}"
            ),
        ]
    )