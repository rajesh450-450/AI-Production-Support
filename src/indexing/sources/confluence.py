import os
import re
import unicodedata

from bs4 import BeautifulSoup
from atlassian import Confluence

from src.indexing.models import SourceDocument
from src.indexing.sources.base import KnowledgeSource
from src.indexing.text_cleaner import normalize_text
from src.config.settings import settings


class ConfluenceSource(KnowledgeSource):
    """
    Extracts knowledge from Confluence Cloud.

    This class is responsible for:
        - loading Confluence pages
        - converting HTML into plain text
        - normalizing Unicode
        - normalizing whitespace

    It does NOT perform document chunking.
    """

    def __init__(
        self,
        url: str | None = None,
        email: str | None = None,
        api_token: str | None = None,
        space_key: str | None = None,
    ):

        self.url = url or settings.atlassian_url
        self.email = email or settings.atlassian_email
        self.api_token = api_token or settings.atlassian_api_token
        self.space_key = space_key or settings.confluence_space_key

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

        if not self.space_key:
            raise ValueError(
                "CONFLUENCE_SPACE_KEY is not configured."
            )

        self.client = Confluence(
            url=self.url,
            username=self.email,
            password=self.api_token,
            cloud=True,
        )

    @property
    def source_name(self) -> str:
        return "confluence"

    @staticmethod
    def _normalize_unicode(text: str) -> str:
        """
        Normalize Unicode characters and remove problematic
        invisible/control characters.

        Keeps normal Unicode characters intact.
        """

        if not text:
            return ""

        # Normalize equivalent Unicode representations.
        text = unicodedata.normalize("NFKC", text)

        cleaned = []

        for char in text:

            category = unicodedata.category(char)

            # Preserve:
            #   newline
            #   carriage return
            #   tab
            if char in "\n\r\t":
                cleaned.append(char)
                continue

            # Remove control characters.
            if category.startswith("C"):
                continue

            cleaned.append(char)

        return "".join(cleaned)

    @staticmethod
    def _normalize_whitespace(text: str) -> str:
        """
        Normalize whitespace while preserving line boundaries.
        """

        if not text:
            return ""

        # Normalize Windows/Mac line endings.
        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

        # Normalize tabs to spaces.
        text = text.replace("\t", " ")

        # Collapse repeated spaces, but preserve newlines.
        text = re.sub(
            r"[^\S\n]+",
            " ",
            text,
        )

        # Remove whitespace surrounding newlines.
        text = re.sub(
            r" *\n *",
            "\n",
            text,
        )

        # Collapse excessive blank lines.
        text = re.sub(
            r"\n{3,}",
            "\n\n",
            text,
        )

        return text.strip()

    def _clean_html(self, html: str) -> str:
        """
        Convert Confluence storage HTML into clean plain text.

        Structural boundaries such as paragraphs and line breaks
        are preserved because they are important to downstream
        document chunking.
        """

        if not html:
            return ""

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        # Explicit HTML line breaks.
        for br in soup.find_all("br"):
            br.replace_with("\n")

        # Block-level elements should create boundaries.
        block_tags = [
            "p",
            "div",
            "section",
            "article",
            "blockquote",
            "pre",
            "ul",
            "ol",
            "li",
            "table",
            "tr",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
        ]

        for tag in soup.find_all(block_tags):
            tag.insert_before("\n")
            tag.insert_after("\n")

        text = soup.get_text(
            separator="",
        )

        text = self._normalize_unicode(text)

        text = self._normalize_whitespace(text)

        return text

    def load(self) -> list[SourceDocument]:
        """
        Load all pages from the configured Confluence space.
        """

        pages = self.client.get_all_pages_from_space(
            space=self.space_key,
            start=0,
            limit=100,
            status="current",
            expand="body.storage,version,history",
        )

        documents = []

        for page in pages:

            page_id = str(page["id"])

            title = page.get("title", "")

            if title == "Overview":
                continue

            body = (
                page.get("body", {})
                .get("storage", {})
                .get("value", "")
            )

            version = page.get("version", {})

            updated_at = version.get("when")

            history = page.get("history", {})

            created_at = history.get("createdDate")

            document = SourceDocument(
                document_id=f"confluence-{page_id}",
                source="confluence",
                external_id=page_id,
                title=title,
                # text=self._clean_html(body),
                text=normalize_text(self._clean_html(body)),
                metadata={
                    "space_key": self.space_key,
                    "url": (
                        f"{self.url}/wiki"
                        f"/spaces/{self.space_key}"
                        f"/pages/{page_id}"
                    ),
                },
                created_at=created_at,
                updated_at=updated_at,
            )

            documents.append(document)

        return documents