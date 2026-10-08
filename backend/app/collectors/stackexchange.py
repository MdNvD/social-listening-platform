from datetime import datetime, timezone
from typing import List, Set

import requests
from bs4 import BeautifulSoup

from app.collectors.base import BaseCollector
from app.collectors.models import CollectedMention


class StackExchangeCollector(BaseCollector):
    """
    Collect public questions from multiple Stack Exchange sites.

    The collector searches several relevant communities and
    normalizes the results into CollectedMention objects.

    Relevance filtering and deduplication are handled later
    by the processing pipeline.
    """

    SEARCH_URL = (
        "https://api.stackexchange.com/2.3/search/advanced"
    )

    SITES = [
        "stackoverflow",
        "superuser",
        "askubuntu",
        "android",
        "arqade",
    ]

    def __init__(
        self,
        timeout: int = 10,
    ):
        self.timeout = timeout

    @property
    def source_name(self) -> str:
        return "stackexchange"

    # =========================================================
    # COLLECT
    # =========================================================

    def collect(
        self,
        keyword: str,
        limit: int = 50,
    ) -> List[CollectedMention]:

        keyword = keyword.strip()

        if not keyword:
            return []

        mentions: List[CollectedMention] = []

        seen_ids: Set[str] = set()

        # We divide the requested limit across sites.
        per_site_limit = max(
            1,
            (limit + len(self.SITES) - 1)
            // len(self.SITES),
        )

        for site in self.SITES:

            if len(mentions) >= limit:
                break

            try:

                response = requests.get(
                    self.SEARCH_URL,
                    params={
                        "site": site,
                        "q": keyword,
                        "sort": "relevance",
                        "order": "desc",
                        "pagesize": min(
                            per_site_limit,
                            100,
                        ),
                    },
                    headers={
                        "User-Agent": (
                            "SocialListeningPlatform/1.0 "
                            "(internship project)"
                        )
                    },
                    timeout=(5, self.timeout),
                )

                response.raise_for_status()

                data = response.json()

            except requests.RequestException as error:

                print(
                    f"Stack Exchange collection failed "
                    f"on {site} for '{keyword}': "
                    f"{type(error).__name__}: {error}"
                )

                continue

            except ValueError as error:

                print(
                    f"Stack Exchange returned invalid JSON "
                    f"on {site} for '{keyword}': {error}"
                )

                continue

            # =================================================
            # API ERROR
            # =================================================

            if data.get("error_id"):

                print(
                    f"Stack Exchange API error on {site}: "
                    f"{data.get('error_name')} - "
                    f"{data.get('error_message')}"
                )

                continue

            items = data.get(
                "items",
                [],
            )

            print(
                f"Stack Exchange [{site}] "
                f"results for '{keyword}': "
                f"{len(items)}"
            )

            # =================================================
            # PROCESS RESULTS
            # =================================================

            for question in items:

                if len(mentions) >= limit:
                    break

                question_id = question.get(
                    "question_id"
                )

                if question_id is None:
                    continue

                question_id = (
                    f"{site}:{question_id}"
                )

                # Prevent duplicates across sites.
                if question_id in seen_ids:
                    continue

                seen_ids.add(
                    question_id
                )

                # -------------------------------------------------
                # TITLE
                # -------------------------------------------------

                title = self._clean_html(
                    question.get(
                        "title"
                    ) or ""
                )

                # -------------------------------------------------
                # BODY
                # -------------------------------------------------

                body = self._clean_html(
                    question.get(
                        "body"
                    ) or ""
                )

                # -------------------------------------------------
                # URL
                # -------------------------------------------------

                link = (
                    question.get(
                        "link"
                    ) or ""
                ).strip()

                if not link:

                    raw_question_id = (
                        question.get(
                            "question_id"
                        )
                    )

                    link = (
                        f"https://{site}.stackexchange.com/"
                        f"questions/{raw_question_id}"
                    )

                # -------------------------------------------------
                # CONTENT
                # -------------------------------------------------

                content = body or title

                if not content:
                    continue

                # -------------------------------------------------
                # AUTHOR
                # -------------------------------------------------

                owner = (
                    question.get(
                        "owner"
                    )
                    or {}
                )

                author = (
                    owner.get(
                        "display_name"
                    )
                    or owner.get(
                        "user_id"
                    )
                )

                if author is not None:
                    author = str(
                        author
                    )

                # -------------------------------------------------
                # DATE
                # -------------------------------------------------

                published_at = (
                    self._from_unix_timestamp(
                        question.get(
                            "creation_date"
                        )
                    )
                )

                # -------------------------------------------------
                # ENGAGEMENT
                # -------------------------------------------------

                score = int(
                    question.get(
                        "score",
                        0,
                    )
                    or 0
                )

                answer_count = int(
                    question.get(
                        "answer_count",
                        0,
                    )
                    or 0
                )

                engagement = (
                    max(score, 0)
                    + answer_count
                )

                # -------------------------------------------------
                # SOURCE ID
                # -------------------------------------------------

                raw_id = str(
                    question.get(
                        "question_id"
                    )
                )

                # -------------------------------------------------
                # CREATE MENTION
                # -------------------------------------------------

                mention = CollectedMention(
                    source="stackexchange",
                    source_id=(
                        f"{site}:{raw_id}"
                    ),
                    url=link,
                    title=title or None,
                    content=content,
                    author=author,
                    published_at=published_at,
                    keyword=keyword,
                    engagement=engagement,
                )

                mentions.append(
                    mention
                )

        print(
            f"Stack Exchange total unique "
            f"questions collected: {len(mentions)}"
        )

        return mentions[:limit]

    # =========================================================
    # HTML CLEANING
    # =========================================================

    @staticmethod
    def _clean_html(
        value: str,
    ) -> str:

        if not value:
            return ""

        soup = BeautifulSoup(
            value,
            "html.parser",
        )

        return soup.get_text(
            " ",
            strip=True,
        )

    # =========================================================
    # UNIX TIMESTAMP
    # =========================================================

    @staticmethod
    def _from_unix_timestamp(
        value,
    ) -> datetime | None:

        if value is None:
            return None

        try:

            return datetime.fromtimestamp(
                int(value),
                tz=timezone.utc,
            )

        except (
            TypeError,
            ValueError,
            OverflowError,
        ):

            return None