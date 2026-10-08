from datetime import datetime, timezone
from typing import List, Set

import requests
from bs4 import BeautifulSoup

from app.collectors.base import BaseCollector
from app.collectors.models import CollectedMention


class HackerNewsCollector(BaseCollector):
    """
    Collect Hacker News stories using the Algolia API.

    The collector creates several focused query variations so that
    different keyword formats can be discovered.

    Examples:

        Samsung Galaxy S26
        Samsung S26
        Galaxy S26
        Samsung Galaxy
        Galaxy S26 Ultra

    The collector does NOT make the final relevance decision.

    Final relevance decisions are handled by RelevanceService.
    """

    SEARCH_URL = (
        "https://hn.algolia.com/api/v1/search_by_date"
    )

    def __init__(
        self,
        timeout: int = 10,
    ):
        self.timeout = timeout

    @property
    def source_name(self) -> str:
        return "hackernews"

    # =========================================================
    # COLLECT
    # =========================================================

    def collect(
        self,
        keyword: str,
        limit: int = 50,
    ) -> List[CollectedMention]:
        """
        Collect Hacker News stories matching the keyword.

        Multiple query variations are searched.

        Duplicate Hacker News stories are removed using
        their Hacker News object ID.
        """

        keyword = keyword.strip()

        if not keyword:
            return []

        queries = self._build_queries(
            keyword
        )

        if not queries:
            return []

        print(
            "\nHacker News queries:"
        )

        for query in queries:
            print(
                f"  - {query}"
            )

        mentions: List[CollectedMention] = []

        # Prevent the same story from being returned
        # multiple times by different queries.
        seen_ids: Set[str] = set()

        # Give every query enough results to provide
        # useful coverage.
        per_query_limit = max(
            10,
            (limit // len(queries)) + 5,
        )

        for query in queries:

            if len(mentions) >= limit:
                break

            try:

                response = requests.get(
                    self.SEARCH_URL,
                    params={
                        "query": query,
                        "tags": "story",
                        "hitsPerPage": per_query_limit,
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
                    "Hacker News collection failed "
                    f"for query '{query}': "
                    f"{type(error).__name__}: "
                    f"{error}"
                )

                continue

            hits = data.get(
                "hits",
                [],
            )

            print(
                f"Hacker News query "
                f"'{query}' returned "
                f"{len(hits)} results."
            )

            for story in hits:

                if len(mentions) >= limit:
                    break

                story_id = story.get(
                    "objectID"
                )

                if story_id is None:
                    continue

                story_id = str(
                    story_id
                )

                # -------------------------------------------------
                # Remove duplicates returned by different queries.
                # -------------------------------------------------

                if story_id in seen_ids:
                    continue

                seen_ids.add(
                    story_id
                )

                # -------------------------------------------------
                # Title
                # -------------------------------------------------

                title = self._clean_html(
                    story.get(
                        "title"
                    ) or ""
                )

                # -------------------------------------------------
                # Story text
                # -------------------------------------------------

                story_text = self._clean_html(
                    story.get(
                        "story_text"
                    ) or ""
                )

                # -------------------------------------------------
                # Prefer original article URL.
                # -------------------------------------------------

                url = (
                    story.get(
                        "url"
                    )
                    or ""
                ).strip()

                # Some Hacker News stories do not have
                # an external article URL.
                #
                # In that case use the Hacker News
                # discussion URL.
                if not url:

                    url = (
                        "https://news.ycombinator.com/"
                        f"item?id={story_id}"
                    )

                # -------------------------------------------------
                # Published timestamp
                # -------------------------------------------------

                published_at = (
                    self._parse_timestamp(
                        story.get(
                            "created_at"
                        )
                    )
                )

                # -------------------------------------------------
                # Content fallback
                # -------------------------------------------------

                content = (
                    story_text
                    or title
                )

                if not content:
                    continue

                # -------------------------------------------------
                # Engagement
                # -------------------------------------------------

                engagement = (
                    story.get(
                        "points",
                        0,
                    )
                    or 0
                )

                # -------------------------------------------------
                # Create mention
                # -------------------------------------------------

                mention = CollectedMention(
                    source="hackernews",
                    source_id=story_id,
                    url=url,
                    title=title or None,
                    content=content,
                    author=story.get(
                        "author"
                    ),
                    published_at=published_at,
                    keyword=keyword,
                    engagement=engagement,
                )

                mentions.append(
                    mention
                )

        print(
            "Hacker News total unique "
            f"mentions collected: "
            f"{len(mentions)}"
        )

        return mentions[:limit]

    # =========================================================
    # QUERY GENERATION
    # =========================================================

    @staticmethod
    def _build_queries(
        keyword: str,
    ) -> List[str]:
        """
        Generate multiple focused Hacker News queries.

        Example:

            Samsung Galaxy S26

        Generates variations such as:

            Samsung Galaxy S26
            Samsung S26
            Galaxy S26
            Samsung Galaxy
            Samsung Galaxy S26
            Galaxy S26

        Duplicate queries are removed.

        For a one-word keyword such as:

            LLM

        only:

            LLM

        is generated.

        We intentionally avoid searching only a model number
        such as:

            S26

        because this can produce unrelated results.
        """

        keyword = keyword.strip()

        if not keyword:
            return []

        words = keyword.split()

        queries: List[str] = []

        # ---------------------------------------------------------
        # Add query helper
        # ---------------------------------------------------------

        def add_query(
            value: str,
        ) -> None:

            value = value.strip()

            if not value:
                return

            existing = {
                query.lower()
                for query in queries
            }

            if value.lower() not in existing:
                queries.append(
                    value
                )

        # ---------------------------------------------------------
        # 1. Original complete keyword
        # ---------------------------------------------------------

        add_query(
            keyword
        )

        # One-word searches don't need additional
        # combinations.
        if len(words) == 1:
            return queries

        # ---------------------------------------------------------
        # 2. First + last word
        #
        # Samsung Galaxy S26
        #       ↓
        # Samsung S26
        # ---------------------------------------------------------

        add_query(
            " ".join(
                [
                    words[0],
                    words[-1],
                ]
            )
        )

        # ---------------------------------------------------------
        # 3. Last two words
        #
        # Samsung Galaxy S26
        #       ↓
        # Galaxy S26
        # ---------------------------------------------------------

        if len(words) >= 3:

            add_query(
                " ".join(
                    words[-2:]
                )
            )

        # ---------------------------------------------------------
        # 4. First two words
        #
        # Samsung Galaxy S26
        #       ↓
        # Samsung Galaxy
        # ---------------------------------------------------------

        if len(words) >= 3:

            add_query(
                " ".join(
                    words[:2]
                )
            )

        # ---------------------------------------------------------
        # 5. First two + last word
        #
        # Samsung Galaxy S26
        #       ↓
        # Samsung Galaxy S26
        #
        # Useful when the original keyword contains
        # extra descriptive terms.
        # ---------------------------------------------------------

        if len(words) >= 4:

            add_query(
                " ".join(
                    words[:2]
                    + words[-1:]
                )
            )

        # ---------------------------------------------------------
        # 6. Last three words
        #
        # Useful for longer product names.
        #
        # Example:
        #
        # Google Pixel 10 Pro XL
        #       ↓
        # Pixel 10 Pro XL
        # ---------------------------------------------------------

        if len(words) >= 4:

            add_query(
                " ".join(
                    words[-3:]
                )
            )

        # ---------------------------------------------------------
        # 7. Remove common stop words
        #
        # Example:
        #
        # "best phone for Samsung Galaxy S26"
        #
        # becomes:
        #
        # "best phone Samsung Galaxy S26"
        #
        # This is still only candidate collection.
        # RelevanceService makes the final decision.
        # ---------------------------------------------------------

        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "for",
            "of",
            "to",
            "in",
            "on",
            "with",
            "is",
            "are",
            "was",
            "were",
            "from",
            "about",
            "review",
            "reviews",
        }

        meaningful_words = [
            word
            for word in words
            if word.lower()
            not in stop_words
        ]

        if (
            len(meaningful_words)
            >= 2
            and len(meaningful_words)
            < len(words)
        ):

            add_query(
                " ".join(
                    meaningful_words
                )
            )

        # ---------------------------------------------------------
        # 8. Important numeric/model terms
        #
        # For:
        #
        # Samsung Galaxy S26 Ultra
        #
        # the model-aware combinations remain:
        #
        # Samsung S26
        # Galaxy S26
        # S26 Ultra
        #
        # We do NOT search "S26" alone.
        # ---------------------------------------------------------

        numeric_words = [
            word
            for word in words
            if any(
                character.isdigit()
                for character in word
            )
        ]

        for numeric_word in numeric_words:

            if len(words) >= 2:

                # Brand/product + model
                add_query(
                    " ".join(
                        [
                            words[0],
                            numeric_word,
                        ]
                    )
                )

            # Model + immediately following descriptor.
            model_index = None

            for index, word in enumerate(words):

                if (
                    word.lower()
                    == numeric_word.lower()
                ):
                    model_index = index
                    break

            if (
                model_index is not None
                and model_index
                < len(words) - 1
            ):

                add_query(
                    " ".join(
                        [
                            numeric_word,
                            words[
                                model_index + 1
                            ],
                        ]
                    )
                )

        return queries

    # =========================================================
    # HTML CLEANING
    # =========================================================

    @staticmethod
    def _clean_html(
        value: str,
    ) -> str:
        """
        Remove HTML markup from Hacker News text.
        """

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
    # TIMESTAMP PARSING
    # =========================================================

    @staticmethod
    def _parse_timestamp(
        timestamp: str | None,
    ) -> datetime | None:
        """
        Convert Hacker News timestamp to UTC datetime.
        """

        if not timestamp:
            return None

        try:

            return (
                datetime.fromisoformat(
                    timestamp.replace(
                        "Z",
                        "+00:00",
                    )
                )
                .astimezone(
                    timezone.utc
                )
            )

        except ValueError:

            return None