from atlassian import Jira

from src.indexing.models import SourceDocument
from src.indexing.sources.base import KnowledgeSource
from src.config.settings import settings


class JiraSource(KnowledgeSource):
    """
    Extracts knowledge from Jira Cloud.

    This class only extracts and normalizes Jira issues
    into SourceDocument objects.
    """

    def __init__(
        self,
        url: str | None = None,
        email: str | None = None,
        api_token: str | None = None,
        project_key: str | None = None,
    ):

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

    @property
    def source_name(self) -> str:
        return "jira"

    def load(self) -> list[SourceDocument]:
        """
        Load Jira issues from the configured project.
        """

        jql = (
            f'project = "{self.project_key}" '
            "ORDER BY updated DESC"
        )

        issues = self.client.jql(
            jql,
            limit=100,
        )

        documents = []

        for issue in issues.get("issues", []):

            issue_id = str(issue["id"])

            issue_key = issue["key"]

            fields = issue.get("fields", {})

            summary = fields.get(
                "summary",
                "",
            )

            description = fields.get(
                "description",
                "",
            )

            issue_type = fields.get(
                "issuetype",
                {},
            ).get(
                "name",
                "",
            )

            status = fields.get(
                "status",
                {},
            ).get(
                "name",
                "",
            )

            priority = fields.get(
                "priority",
                {},
            )

            priority_name = (
                priority.get("name", "")
                if priority
                else ""
            )

            created_at = fields.get(
                "created"
            )

            updated_at = fields.get(
                "updated"
            )

            text_parts = [
                f"Summary: {summary}",
                f"Issue Type: {issue_type}",
                f"Status: {status}",
                f"Priority: {priority_name}",
            ]

            if description:
                text_parts.append(
                    f"Description: {description}"
                )

            text = "\n".join(text_parts)

            document = SourceDocument(
                document_id=f"jira-{issue_key}",
                source="jira",
                external_id=issue_id,
                title=summary,
                text=text,
                metadata={
                    "project_key": self.project_key,
                    "issue_key": issue_key,
                    "issue_type": issue_type,
                    "status": status,
                    "priority": priority_name,
                    "url": (
                        f"{self.url}/browse/"
                        f"{issue_key}"
                    ),
                },
                created_at=created_at,
                updated_at=updated_at,
            )

            documents.append(document)

        return documents