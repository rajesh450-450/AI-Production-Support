from typing import Any

from atlassian import Jira
from src.config.settings import settings


class JiraService:
    """
    Provides live operational access to Jira Cloud.

    This service is separate from JiraSource.

    JiraSource:
        Loads Jira data for indexing.

    JiraService:
        Performs live Jira operations.
    """

    def __init__(
        self,
        url: str | None = None,
        email: str | None = None,
        api_token: str | None = None,
        project_key: str | None = None,
    ) -> None:

        self.url = url or settings.atlassian_url
        self.email = email or settings.atlassian_email
        self.api_token = api_token or settings.atlassian_api_token
        self.project_key = project_key or settings.jira_project_key

        if not self.url:
            raise ValueError(
                "ATLASSIAN_URL is not configured."
            )

        if not self.email:
            raise ValueError(
                "ATLASSIAN_EMAIL is not configured."
            )

        if not self.api_token:
            raise ValueError(
                "ATLASSIAN_API_TOKEN is not configured."
            )

        if not self.project_key:
            raise ValueError(
                "JIRA_PROJECT_KEY is not configured."
            )

        self.client = Jira(
            url=self.url,
            username=self.email,
            password=self.api_token,
            cloud=True,
        )

    # =====================================================
    # SEARCH ISSUES
    # =====================================================

    def search_issues(
        self,
        jql: str,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """
        Execute a JQL query against live Jira.
        """

        response = self.client.jql(
            jql,
            limit=limit,
        )

        if not response:
            return []

        return response.get(
            "issues",
            [],
        )

    # =====================================================
    # RESOLVE USER
    # =====================================================

    def resolve_user(
        self,
        name: str,
    ) -> dict[str, Any] | None:
        """
        Resolve a Jira user by display name/search text.

        Jira Cloud uses account IDs for user identity.
        """

        users = self.client.user_find_by_user_string(
            query=name,
        )

        if not users:
            return None

        name_lower = name.strip().lower()

        # Prefer exact display-name match.
        for user in users:

            display_name = (
                user.get("displayName", "")
                .strip()
                .lower()
            )

            if display_name == name_lower:
                return user

        # Otherwise use the first matching active user.
        for user in users:

            if user.get("active", True):
                return user

        return users[0]

    # =====================================================
    # ISSUES ASSIGNED TO USER
    # =====================================================

    def get_issues_assigned_to(
        self,
        assignee: str,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """
        Return currently open/in-progress issues assigned
        to the specified Jira user.
        """

        user = self.resolve_user(
            assignee
        )

        if user is None:
            raise ValueError(
                f"Jira user '{assignee}' could not be found."
            )

        account_id = user.get(
            "accountId"
        )

        if not account_id:
            raise ValueError(
                f"Could not resolve Jira account ID for "
                f"user '{assignee}'."
            )

        jql = (
            f'project = "{self.project_key}" '
            f'AND assignee = "{account_id}" '
            f'AND statusCategory != Done '
            f'ORDER BY updated DESC'
        )

        return self.search_issues(
            jql=jql,
            limit=limit,
        )

    # =====================================================
    # OPEN / IN PROGRESS
    # =====================================================

    def get_open_inprogress_issues(
        self,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """
        Return currently open or in-progress Jira issues.
        """

        jql = (
            f'project = "{self.project_key}" '
            'AND statusCategory != Done '
            'ORDER BY updated DESC'
        )

        return self.search_issues(
            jql=jql,
            limit=limit,
        )

    # =====================================================
    # CREATE ISSUE
    # =====================================================

    def create_issue(
        self,
        summary: str,
        description: str,
        issue_type: str = "Task",
        project_key: str | None = None,
    ) -> dict[str, Any]:
        """
        Create a Jira issue.
        """

        project = (
            project_key
            or self.project_key
        )

        fields = {
            "project": {
                "key": project,
            },
            "summary": summary,
            "description": description,
            "issuetype": {
                "name": issue_type,
            },
        }

        return self.client.issue_create(
            fields=fields
        )