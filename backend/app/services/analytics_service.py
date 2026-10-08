from collections import Counter

from sqlalchemy.orm import Session

from app.database.models import (
    Mention,
    MentionAnalysis,
    Search,
)


class AnalyticsService:
    """
    Calculates keyword-level analytics for the dashboard.

    A Search represents one collection run.

    The Dashboard represents the accumulated social-listening
    data for the selected keyword across all completed searches.

    Example:

        Search #80 -> Samsung Galaxy S26
        Search #84 -> Samsung Galaxy S26
        Search #88 -> Samsung Galaxy S26
        Search #90 -> Samsung Galaxy S26

    The dashboard combines the relevant unique mentions from
    these completed searches.

    Important distinction:

        total_collected
            Raw mentions collected during the selected search.

        total_processed
            Relevant unique mentions newly saved during the
            selected search.

        total_mentions
            Accumulated unique relevant mentions for the keyword.
    """

    def get_search_analytics(
        self,
        db: Session,
        search_id: int,
    ):
        # =========================================================
        # Find selected search
        # =========================================================

        search = (
            db.query(Search)
            .filter(
                Search.id == search_id
            )
            .first()
        )

        if search is None:
            return None

        # =========================================================
        # Find all completed searches for the same keyword
        # =========================================================

        searches = (
            db.query(Search)
            .filter(
                Search.keyword.ilike(
                    search.keyword
                )
            )
            .filter(
                Search.status == "completed"
            )
            .all()
        )

        search_ids = [
            item.id
            for item in searches
        ]

        # =========================================================
        # No completed searches
        # =========================================================

        if not search_ids:
            return {
                "search_id": search.id,
                "keyword": search.keyword,

                "total_collected": (
                    search.total_collected or 0
                ),

                "total_processed": (
                    search.total_processed or 0
                ),

                "total_mentions": 0,

                "sentiment_distribution": [],
                "topic_distribution": [],
                "source_distribution": [],
                "mentions_over_time": [],

                "first_mention_at": None,
                "last_mention_at": None,
            }

        # =========================================================
        # Get relevant, non-duplicate mentions
        # =========================================================

        rows = (
            db.query(
                Mention,
                MentionAnalysis,
            )
            .join(
                MentionAnalysis,
                Mention.id
                == MentionAnalysis.mention_id,
            )
            .filter(
                Mention.search_id.in_(
                    search_ids
                )
            )
            .filter(
                MentionAnalysis.is_relevant.is_(True)
            )
            .filter(
                MentionAnalysis.is_duplicate.is_(False)
            )
            .all()
        )

        # =========================================================
        # Cross-search deduplication
        # =========================================================
        #
        # This protects analytics from duplicate mentions that
        # may have been collected during different scheduled runs.
        #
        # Priority:
        #
        # 1. source + source_id
        # 2. source + URL
        # =========================================================

        unique_rows = []

        seen_source_ids = set()
        seen_source_urls = set()

        for mention, analysis in rows:

            source = (
                mention.source
                or "unknown"
            )

            # -----------------------------------------------------
            # Source + source ID
            # -----------------------------------------------------

            if mention.source_id:

                source_id_key = (
                    source,
                    str(
                        mention.source_id
                    ),
                )

                if (
                    source_id_key
                    in seen_source_ids
                ):
                    continue

                seen_source_ids.add(
                    source_id_key
                )

            # -----------------------------------------------------
            # Source + URL fallback
            # -----------------------------------------------------

            elif mention.url:

                source_url_key = (
                    source,
                    mention.url,
                )

                if (
                    source_url_key
                    in seen_source_urls
                ):
                    continue

                seen_source_urls.add(
                    source_url_key
                )

            # -----------------------------------------------------
            # Keep unique mention
            # -----------------------------------------------------

            unique_rows.append(
                (
                    mention,
                    analysis,
                )
            )

        # =========================================================
        # Counters
        # =========================================================

        sentiment_counter = Counter()
        topic_counter = Counter()
        source_counter = Counter()
        date_counter = Counter()

        published_dates = []

        # =========================================================
        # Process unique mentions
        # =========================================================

        for mention, analysis in unique_rows:

            # -----------------------------------------------------
            # Source
            # -----------------------------------------------------

            if mention.source:

                source_counter[
                    mention.source
                ] += 1

            # -----------------------------------------------------
            # Sentiment
            # -----------------------------------------------------

            if analysis.sentiment:

                sentiment_counter[
                    analysis.sentiment
                ] += 1

            # -----------------------------------------------------
            # Topic
            # -----------------------------------------------------

            if analysis.topic:

                topic_counter[
                    analysis.topic
                ] += 1

            # -----------------------------------------------------
            # Publication date
            # -----------------------------------------------------

            if mention.published_at:

                date_key = (
                    mention.published_at
                    .date()
                    .isoformat()
                )

                date_counter[
                    date_key
                ] += 1

                published_dates.append(
                    mention.published_at
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
            in sorted(
                source_counter.items(),
                key=lambda item: (
                    -item[1],
                    item[0],
                ),
            )
        ]

        # =========================================================
        # Sentiment distribution
        # =========================================================

        sentiment_distribution = [
            {
                "sentiment": sentiment,
                "count": count,
            }
            for sentiment, count
            in sorted(
                sentiment_counter.items(),
                key=lambda item: (
                    -item[1],
                    item[0],
                ),
            )
        ]

        # =========================================================
        # Topic distribution
        # =========================================================

        topic_distribution = [
            {
                "topic": topic,
                "count": count,
            }
            for topic, count
            in sorted(
                topic_counter.items(),
                key=lambda item: (
                    -item[1],
                    item[0],
                ),
            )
        ]

        # =========================================================
        # Mentions over time
        # =========================================================

        mentions_over_time = [
            {
                "date": date,
                "count": date_counter[date],
            }
            for date in sorted(
                date_counter.keys()
            )
        ]

        # =========================================================
        # First / last mention
        # =========================================================

        first_mention_at = None
        last_mention_at = None

        if published_dates:

            first_mention_at = min(
                published_dates
            )

            last_mention_at = max(
                published_dates
            )

        # =========================================================
        # Return analytics
        # =========================================================

        return {
            "search_id": search.id,

            "keyword": search.keyword,

            # -----------------------------------------------------
            # Current search run
            # -----------------------------------------------------

            "total_collected": (
                search.total_collected or 0
            ),

            "total_processed": (
                search.total_processed or 0
            ),

            # -----------------------------------------------------
            # Accumulated keyword-level data
            # -----------------------------------------------------

            "total_mentions": len(
                unique_rows
            ),

            "sentiment_distribution": (
                sentiment_distribution
            ),

            "topic_distribution": (
                topic_distribution
            ),

            "source_distribution": (
                source_distribution
            ),

            "mentions_over_time": (
                mentions_over_time
            ),

            "first_mention_at": (
                first_mention_at
            ),

            "last_mention_at": (
                last_mention_at
            ),
        }