import re
from datetime import datetime, timezone
from typing import List

import feedparser
from bs4 import BeautifulSoup

from app.collectors.base import BaseCollector
from app.collectors.models import CollectedMention


class RSSCollector(BaseCollector):
    """
    Collect candidate articles from public RSS feeds.

    RSS responsibilities:
    - Read configured RSS feeds
    - Examine recent feed entries
    - Perform broad candidate matching
    - Extract article metadata
    - Clean HTML
    - Return candidate mentions

    Important:
    RSS matching is intentionally broader than the final
    RelevanceService.

    The RSS collector should avoid rejecting legitimate
    wording variations too early.

    Example:

        Search:
            Apple 18 Pro Max

        Article:
            iPhone 18 Pro Max

    This article should be allowed through RSS candidate
    collection so that the final RelevanceService can make
    the stricter relevance decision.
    """

    def __init__(
        self,
        feed_urls: List[str],
    ):
        self.feed_urls = feed_urls

    @property
    def source_name(self) -> str:
        return "rss"

    def collect(
        self,
        keyword: str,
        limit: int = 50,
    ) -> List[CollectedMention]:

        keyword = keyword.strip()

        if not keyword:
            return []

        all_candidates: List[CollectedMention] = []

        feed_count = len(self.feed_urls)

        if feed_count == 0:
            return []

        # Give every configured feed an opportunity to
        # contribute results.
        feed_limit = max(
            1,
            (limit + feed_count - 1)
            // feed_count,
        )

        for feed_url in self.feed_urls:

            if len(all_candidates) >= limit:
                break

            print(
                f"RSS feed: {feed_url}"
            )

            try:

                feed = feedparser.parse(
                    feed_url
                )

                if getattr(
                    feed,
                    "bozo",
                    False,
                ):
                    print(
                        "RSS warning: "
                        f"Feed may contain malformed data: "
                        f"{feed_url}"
                    )

                entries = getattr(
                    feed,
                    "entries",
                    [],
                )

                print(
                    f"RSS entries found: "
                    f"{len(entries)}"
                )

                feed_candidates = 0

                for entry in entries:

                    if feed_candidates >= feed_limit:
                        break

                    mention = (
                        self._entry_to_mention(
                            entry=entry,
                            keyword=keyword,
                        )
                    )

                    if mention is None:
                        continue

                    # RSS performs only broad candidate
                    # matching.
                    #
                    # The final relevance decision is
                    # still performed by RelevanceService.
                    if not self._is_candidate_match(
                        mention,
                        keyword,
                    ):
                        continue

                    all_candidates.append(
                        mention
                    )

                    feed_candidates += 1

                    if len(all_candidates) >= limit:
                        break

                print(
                    f"RSS candidates from feed: "
                    f"{feed_candidates}"
                )

            except Exception as error:

                print(
                    f"RSS collector error for "
                    f"{feed_url}: "
                    f"{type(error).__name__}: "
                    f"{error}"
                )

                continue

        return all_candidates[:limit]

    # ==================================================
    # CANDIDATE MATCHING
    # ==================================================

    @classmethod
    def _is_candidate_match(
        cls,
        mention: CollectedMention,
        keyword: str,
    ) -> bool:
        """
        Perform broad candidate matching.

        This stage should be permissive.

        The final RelevanceService is responsible for
        deciding whether a mention is actually relevant.

        Examples:

            Search:
                Samsung Galaxy S26

            Possible candidates:

                Samsung Galaxy S26
                Samsung S26
                Galaxy S26
                Galaxy S26 Ultra
                Samsung's Galaxy S26

            Search:
                Apple 18 Pro Max

            Possible candidates:

                Apple 18 Pro Max
                iPhone 18 Pro Max
                iPhone 18 Pro
                Apple iPhone 18
                iPhone 18 Max

        The candidate collector should not reject these
        variations too aggressively.
        """

        keyword_terms = cls._extract_terms(
            keyword
        )

        if not keyword_terms:
            return False

        title = cls._normalize_text(
            mention.title or ""
        )

        content = cls._normalize_text(
            mention.content or ""
        )

        searchable_text = (
            f"{title} {content}"
        ).strip()

        if not searchable_text:
            return False

        # --------------------------------------------------
        # 1. Exact phrase
        # --------------------------------------------------

        normalized_keyword = (
            cls._normalize_text(keyword)
        )

        if (
            normalized_keyword
            and normalized_keyword
            in searchable_text
        ):
            return True

        # --------------------------------------------------
        # 2. Generate search variants
        # --------------------------------------------------

        search_variants = (
            cls._build_term_variants(
                keyword_terms
            )
        )

        # --------------------------------------------------
        # 3. Check important/model terms
        # --------------------------------------------------

        important_terms = (
            cls._identify_important_terms(
                keyword_terms
            )
        )

        important_matches = []

        for term in important_terms:

            variants = search_variants.get(
                term,
                [term],
            )

            if any(
                cls._term_exists(
                    variant,
                    searchable_text,
                )
                for variant in variants
            ):
                important_matches.append(
                    term
                )

        # If the keyword contains a model/product
        # identifier such as:
        #
        # S26
        # 18
        # 17
        # M4
        #
        # require that identifier.
        if important_terms:

            if not important_matches:
                return False

        # --------------------------------------------------
        # 4. Count matched keyword concepts
        # --------------------------------------------------

        matched_terms = []

        for term in keyword_terms:

            variants = search_variants.get(
                term,
                [term],
            )

            matched = any(
                cls._term_exists(
                    variant,
                    searchable_text,
                )
                for variant in variants
            )

            if matched:
                matched_terms.append(
                    term
                )

        matched_count = len(
            matched_terms
        )

        total_terms = len(
            keyword_terms
        )

        # --------------------------------------------------
        # 5. One-word searches
        # --------------------------------------------------

        if total_terms == 1:

            return matched_count == 1

        # --------------------------------------------------
        # 6. Two-word searches
        # --------------------------------------------------

        if total_terms == 2:

            # Require both terms for normal two-word
            # searches.
            return (
                matched_count == 2
            )

        # --------------------------------------------------
        # 7. Three-or-more word searches
        # --------------------------------------------------
        #
        # For longer product names, articles frequently
        # omit brand words or use alternate terminology.
        #
        # Example:
        #
        # Search:
        #     Apple 18 Pro Max
        #
        # Article:
        #     iPhone 18 Pro Max
        #
        # "Apple" may not appear, but:
        #
        #     18
        #     Pro
        #     Max
        #
        # do.
        #
        # Therefore we require:
        #
        # - the model/number when one exists
        # - at least 60% of the searchable concepts
        #
        # Final RelevanceService remains the strict filter.

        minimum_matches = max(
            2,
            int(
                total_terms * 0.60
                + 0.999
            ),
        )

        return (
            matched_count
            >= minimum_matches
        )

    # ==================================================
    # TERM EXTRACTION
    # ==================================================

    @staticmethod
    def _extract_terms(
        keyword: str,
    ) -> list[str]:
        """
        Extract meaningful search terms.

        Stop words are removed because they generally
        do not help identify the target.
        """

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
            "at",
            "by",
            "from",
            "this",
            "that",
        }

        normalized = re.sub(
            r"[^a-zA-Z0-9\s]+",
            " ",
            keyword,
        )

        terms = []

        for term in normalized.lower().split():

            if not term:
                continue

            if term in stop_words:
                continue

            terms.append(term)

        return terms

    # ==================================================
    # TERM VARIANTS
    # ==================================================

    @staticmethod
    def _build_term_variants(
        terms: list[str],
    ) -> dict[str, list[str]]:
        """
        Build lightweight terminology variants.

        These are intentionally conservative.

        They help candidate collection understand
        common product naming differences without
        making the final relevance decision.
        """

        variants: dict[str, list[str]] = {}

        for term in terms:

            term_variants = {
                term
            }

            # Common Apple terminology.
            if term == "apple":
                term_variants.update(
                    {
                        "apple",
                        "iphone",
                        "ipad",
                        "mac",
                        "macbook",
                    }
                )

            # Common Samsung terminology.
            elif term == "samsung":
                term_variants.update(
                    {
                        "samsung",
                        "galaxy",
                    }
                )

            # Common Google terminology.
            elif term == "google":
                term_variants.update(
                    {
                        "google",
                        "pixel",
                    }
                )

            variants[term] = list(
                term_variants
            )

        return variants

    # ==================================================
    # IMPORTANT TERM DETECTION
    # ==================================================

    @staticmethod
    def _identify_important_terms(
        terms: list[str],
    ) -> list[str]:
        """
        Identify model/product identifiers.

        Terms containing numbers are considered
        important.

        Examples:

            S26 -> important
            18  -> important
            iPhone18 -> important
            M4 -> important
        """

        important_terms = []

        for term in terms:

            if any(
                character.isdigit()
                for character in term
            ):
                important_terms.append(
                    term
                )

        return important_terms

    # ==================================================
    # TERM SEARCH
    # ==================================================

    @staticmethod
    def _term_exists(
        term: str,
        text: str,
    ) -> bool:

        if not term:
            return False

        pattern = (
            rf"\b{re.escape(term)}\b"
        )

        return (
            re.search(
                pattern,
                text,
            )
            is not None
        )

    # ==================================================
    # TEXT NORMALIZATION
    # ==================================================

    @staticmethod
    def _normalize_text(
        value: str,
    ) -> str:
        """
        Normalize text before candidate matching.

        Steps:
        - lowercase
        - remove URLs
        - convert punctuation to spaces
        - normalize whitespace

        Examples:

            "iPhone 18-Pro Max"
                ->
            "iphone 18 pro max"

            "Samsung's Galaxy S26"
                ->
            "samsung s galaxy s26"
        """

        if not value:
            return ""

        value = value.lower()

        # Remove URLs.
        value = re.sub(
            r"https?://\S+",
            " ",
            value,
        )

        # Replace punctuation with spaces.
        value = re.sub(
            r"[^a-z0-9\s]",
            " ",
            value,
        )

        # Collapse whitespace.
        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        return value.strip()

    # ==================================================
    # ENTRY CONVERSION
    # ==================================================

    def _entry_to_mention(
        self,
        entry,
        keyword: str,
    ) -> CollectedMention | None:

        title = self._clean_html(
            entry.get(
                "title",
                "",
            )
        )

        summary = self._clean_html(
            entry.get(
                "summary",
                "",
            )
        )

        content = self._extract_content(
            entry
        )

        link = (
            entry.get(
                "link",
                "",
            )
            or ""
        ).strip()

        if not link:
            return None

        # Use summary when full RSS content
        # is unavailable.
        if not content:
            content = summary

        # Use title as final fallback.
        if not content:
            content = title

        if not title and not content:
            return None

        published_at = (
            self._get_published_time(
                entry
            )
        )

        source_id = (
            entry.get("id")
            or entry.get("guid")
            or link
        )

        author = entry.get(
            "author",
            None,
        )

        return CollectedMention(
            source="rss",
            source_id=str(source_id),
            url=link,
            title=title or None,
            content=content,
            author=author,
            published_at=published_at,
            keyword=keyword,
            engagement=0,
        )

    # ==================================================
    # CONTENT EXTRACTION
    # ==================================================

    @classmethod
    def _extract_content(
        cls,
        entry,
    ) -> str:

        content_items = entry.get(
            "content",
            [],
        )

        if content_items:

            parts = []

            for item in content_items:

                value = item.get(
                    "value",
                    "",
                )

                cleaned = cls._clean_html(
                    value
                )

                if cleaned:
                    parts.append(
                        cleaned
                    )

            if parts:

                return " ".join(
                    parts
                )

        summary = entry.get(
            "summary",
            "",
        )

        return cls._clean_html(
            summary
        )

    # ==================================================
    # HTML CLEANING
    # ==================================================

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

    # ==================================================
    # DATE EXTRACTION
    # ==================================================

    @staticmethod
    def _get_published_time(
        entry,
    ) -> datetime | None:

        parsed_time = (
            entry.get(
                "published_parsed"
            )
            or entry.get(
                "updated_parsed"
            )
        )

        if parsed_time is None:
            return None

        return datetime(
            parsed_time.tm_year,
            parsed_time.tm_mon,
            parsed_time.tm_mday,
            parsed_time.tm_hour,
            parsed_time.tm_min,
            parsed_time.tm_sec,
            tzinfo=timezone.utc,
        )