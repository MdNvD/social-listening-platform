import re
from typing import Optional
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from bs4 import BeautifulSoup

from app.collectors.models import CollectedMention


class NormalizationService:
    """
    Cleans and standardizes collected mentions before
    validation, relevance filtering, deduplication, and storage.
    """

    MAX_TITLE_LENGTH = 500
    MAX_CONTENT_LENGTH = 10000

    TRACKING_PARAMETERS = {
        "utm_source",
        "utm_medium",
        "utm_campaign",
        "utm_term",
        "utm_content",
        "utm_id",
        "gclid",
        "fbclid",
    }

    def normalize(
        self,
        mention: CollectedMention,
    ) -> Optional[CollectedMention]:
        """
        Normalize a collected mention.

        Returns:
            A cleaned CollectedMention, or None if the mention
            is invalid and should not continue through the pipeline.
        """

        url = self.normalize_url(mention.url)

        title = self.clean_text(mention.title)

        content = self.clean_text(mention.content)

        if not url:
            return None

        if not title and not content:
            return None

        title = title[:self.MAX_TITLE_LENGTH]

        content = content[:self.MAX_CONTENT_LENGTH]

        return CollectedMention(
            source=mention.source.strip().lower(),
            source_id=self.clean_optional_string(
                mention.source_id
            ),
            url=url,
            title=title or None,
            content=content,
            author=self.clean_optional_string(
                mention.author
            ),
            published_at=mention.published_at,
            keyword=mention.keyword.strip(),
            engagement=max(mention.engagement, 0),
        )

    @staticmethod
    def clean_text(
        value: Optional[str],
    ) -> str:
        """
        Remove HTML and normalize whitespace.
        """

        if not value:
            return ""

        soup = BeautifulSoup(
            value,
            "html.parser",
        )

        text = soup.get_text(
            " ",
            strip=True,
        )

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip()

    @classmethod
    def normalize_url(
        cls,
        url: Optional[str],
    ) -> str:
        """
        Normalize URLs by removing common tracking parameters.
        """

        if not url:
            return ""

        url = url.strip()

        try:
            parsed = urlparse(url)

            if not parsed.scheme or not parsed.netloc:
                return ""

            query_parameters = parse_qsl(
                parsed.query,
                keep_blank_values=True,
            )

            filtered_parameters = [
                (key, value)
                for key, value in query_parameters
                if key.lower()
                not in cls.TRACKING_PARAMETERS
            ]

            normalized_query = urlencode(
                filtered_parameters,
            )

            normalized = urlunparse(
                (
                    parsed.scheme.lower(),
                    parsed.netloc.lower(),
                    parsed.path,
                    parsed.params,
                    normalized_query,
                    "",
                )
            )

            return normalized.rstrip("/")

        except ValueError:
            return ""

    @staticmethod
    def clean_optional_string(
        value: Optional[str],
    ) -> Optional[str]:
        """
        Clean optional string fields.
        """

        if not value:
            return None

        value = value.strip()

        return value or None