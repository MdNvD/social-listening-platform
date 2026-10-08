from collections import Counter
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.models import (
    Mention,
    MentionAnalysis,
    Search,
)
from app.services.search_service import SearchService
from app.services.search_persistence_service import (
    SearchPersistenceService,
)


class CompetitorService:
    """
    Builds factual comparisons between multiple monitored
    keywords/products/brands.

    Each competitor is processed through the same existing
    collection and NLP pipeline used by normal searches.

    The comparison aggregates all unique stored mentions for
    the requested keyword rather than relying only on the
    latest search run.

    The comparison does NOT assign a winner or ranking.
    It only reports observed collected-data metrics.
    """

    MIN_COMPETITORS = 2
    MAX_COMPETITORS = 5

    def __init__(self):
        self.search_service = SearchService()
        self.persistence_service = SearchPersistenceService()

    # =========================================================
    # Main comparison
    # =========================================================

    def compare(
        self,
        db: Session,
        keywords: list[str],
        limit_per_source: int = 10,
    ) -> dict[str, Any]:

        cleaned_keywords = self._clean_keywords(keywords)

        if len(cleaned_keywords) < self.MIN_COMPETITORS:
            raise ValueError(
                "At least 2 competitors are required."
            )

        if len(cleaned_keywords) > self.MAX_COMPETITORS:
            raise ValueError(
                f"A maximum of {self.MAX_COMPETITORS} "
                "competitors is supported."
            )

        comparisons = []

        for keyword in cleaned_keywords:

            # -----------------------------------------------------
            # Make sure at least one completed search exists.
            #
            # If the keyword has never been searched before,
            # a new search is executed through the normal pipeline.
            # -----------------------------------------------------

            search = self._get_or_create_search(
                db=db,
                keyword=keyword,
                limit_per_source=limit_per_source,
            )

            # -----------------------------------------------------
            # Build comparison from ALL unique stored mentions
            # belonging to this keyword.
            # -----------------------------------------------------

            comparison = self._build_comparison(
                db=db,
                keyword=keyword,
                search=search,
            )

            comparisons.append(comparison)

        return {
            "competitors": comparisons,
            "count": len(comparisons),
        }

    # =========================================================
    # Find existing completed search or create new one
    # =========================================================

    def _get_or_create_search(
        self,
        db: Session,
        keyword: str,
        limit_per_source: int,
    ) -> Search:

        existing_search = (
            db.query(Search)
            .filter(
                Search.keyword.ilike(
                    keyword.strip()
                )
            )
            .filter(
                Search.status == "completed"
            )
            .order_by(
                Search.created_at.desc()
            )
            .first()
        )

        if existing_search is not None:
            return existing_search

        # ---------------------------------------------------------
        # No completed search exists.
        # Run a fresh search using the normal pipeline.
        # ---------------------------------------------------------

        search = Search(
            keyword=keyword.strip(),
            status="pending",
        )

        db.add(search)
        db.commit()
        db.refresh(search)

        try:

            self.persistence_service.mark_search_started(
                db=db,
                search=search,
            )

            result = self.search_service.run_search(
                keyword=keyword,
                limit_per_source=limit_per_source,
            )

            self.persistence_service.save_search_results(
                db=db,
                search=search,
                processed_mentions=result[
                    "processed_mentions"
                ],
                raw_count=len(
                    result["raw_mentions"]
                ),
            )

            self.persistence_service.mark_search_completed(
                db=db,
                search=search,
            )

            db.refresh(search)

            return search

        except Exception:

            db.rollback()

            refreshed_search = (
                db.query(Search)
                .filter(
                    Search.id == search.id
                )
                .first()
            )

            if refreshed_search is not None:

                self.persistence_service.mark_search_failed(
                    db=db,
                    search=refreshed_search,
                )

            raise

    # =========================================================
    # Build comparison metrics
    # =========================================================

    def _build_comparison(
        self,
        db: Session,
        keyword: str,
        search: Search,
    ) -> dict[str, Any]:
        """
        Build comparison metrics from ALL unique stored mentions
        for the supplied keyword.

        This intentionally does NOT filter by search.id.

        Scheduled monitoring creates multiple Search records for
        the same keyword. The persistence layer prevents the same
        source item from being stored repeatedly, so aggregating
        Mention records by keyword gives us the actual unique
        observed dataset for that competitor.
        """

        rows = (
            db.query(
                Mention,
                MentionAnalysis,
            )
            .join(
                MentionAnalysis,
                MentionAnalysis.mention_id
                == Mention.id,
            )
            .filter(
                Mention.keyword.ilike(
                    keyword.strip()
                )
            )
            .filter(
                MentionAnalysis.is_relevant.is_(True)
            )
            .filter(
                MentionAnalysis.is_duplicate.is_(False)
            )
            .order_by(
                Mention.collected_at.desc(),
                Mention.id.desc(),
            )
            .all()
        )

        # ---------------------------------------------------------
        # Counters
        # ---------------------------------------------------------

        sentiment_counter = Counter()
        topic_counter = Counter()
        source_counter = Counter()

        negative_mentions = []

        total_mentions = 0
        total_engagement = 0

        # ---------------------------------------------------------
        # Process all unique relevant non-duplicate mentions
        # ---------------------------------------------------------

        for mention, analysis in rows:

            sentiment = (
                analysis.sentiment
                or "neutral"
            )

            topic = (
                analysis.topic
                or "Other"
            )

            source = (
                mention.source
                or "unknown"
            )

            sentiment_counter[sentiment] += 1
            topic_counter[topic] += 1
            source_counter[source] += 1

            total_mentions += 1

            total_engagement += (
                mention.engagement or 0
            )

            # -----------------------------------------------------
            # Negative mentions
            # -----------------------------------------------------

            if sentiment == "negative":

                negative_mentions.append(
                    {
                        "id": mention.id,
                        "title": (
                            mention.title
                            or mention.content
                        ),
                        "url": mention.url,
                        "source": mention.source,
                        "topic": topic,
                        "sentiment_confidence": (
                            analysis.sentiment_confidence
                        ),
                    }
                )

        # =========================================================
        # Sentiment distribution
        # =========================================================

        sentiment_distribution = [
            {
                "sentiment": sentiment,
                "count": count,
            }
            for sentiment, count
            in sentiment_counter.items()
        ]

        sentiment_distribution.sort(
            key=lambda item: (
                -item["count"],
                item["sentiment"],
            )
        )

        # =========================================================
        # Topic distribution
        # =========================================================

        topic_distribution = [
            {
                "topic": topic,
                "count": count,
            }
            for topic, count
            in topic_counter.items()
        ]

        topic_distribution.sort(
            key=lambda item: (
                -item["count"],
                item["topic"],
            )
        )

        # =========================================================
        # Source distribution
        # =========================================================

        source_distribution = [
            {
                "source": source,
                "count": count,
            }
            for source, count
            in source_counter.items()
        ]

        source_distribution.sort(
            key=lambda item: (
                -item["count"],
                item["source"],
            )
        )

        # =========================================================
        # Negative mentions
        # =========================================================

        negative_mentions.sort(
            key=lambda item: (
                item["sentiment_confidence"]
                or 0
            ),
            reverse=True,
        )

        # =========================================================
        # Final comparison object
        # =========================================================
        #
        # IMPORTANT:
        #
        # total_collected and total_processed here represent the
        # unique stored dataset used for comparison.
        #
        # We intentionally do NOT use:
        #
        #     search.total_collected
        #     search.total_processed
        #
        # because those values belong to one individual search run.
        #
        # A scheduled monitoring keyword can have many Search rows.
        # =========================================================

        return {
            "search_id": search.id,

            "keyword": keyword,

            # Unique stored mentions available for comparison.
            "total_collected": total_mentions,

            # Unique relevant, non-duplicate mentions available
            # for comparison.
            "total_processed": total_mentions,

            "total_mentions": total_mentions,

            "total_engagement": total_engagement,

            "sentiment_distribution": (
                sentiment_distribution
            ),

            "topic_distribution": (
                topic_distribution
            ),

            "source_distribution": (
                source_distribution
            ),

            "negative_mentions": (
                negative_mentions[:10]
            ),
        }

    # =========================================================
    # Clean competitor names
    # =========================================================

    @staticmethod
    def _clean_keywords(
        keywords: list[str],
    ) -> list[str]:

        cleaned = []

        for keyword in keywords:

            if not isinstance(
                keyword,
                str,
            ):
                continue

            keyword = keyword.strip()

            if not keyword:
                continue

            # Case-insensitive duplicate competitor names.
            if any(
                existing.lower()
                == keyword.lower()
                for existing in cleaned
            ):
                continue

            cleaned.append(keyword)

        return cleaned