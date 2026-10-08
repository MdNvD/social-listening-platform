from datetime import datetime
from math import ceil
from typing import Optional

from sqlalchemy import or_, func
from sqlalchemy.orm import Session

from app.database.models import (
    Mention,
    MentionAnalysis,
    Search,
)


class MentionService:
    """
    Retrieves searchable and filterable mentions for an active search keyword.

    The selected search_id is used to identify the active keyword.

    For scheduled monitoring, mentions may belong to multiple Search records
    with the same keyword. Therefore, this service aggregates mentions across
    completed searches for that keyword instead of limiting results to one
    Search ID.

    Supported filters:

    - source
    - sentiment
    - topic
    - start date
    - end date
    - text search

    Results are:

    - Relevant only
    - Non-duplicate only
    - Aggregated across completed searches for the same keyword
    - Deduplicated across repeated scheduled runs
    - Paginated
    - Sorted by publication/collection date
    """

    def get_mentions(
        self,
        db: Session,
        search_id: int,
        page: int = 1,
        page_size: int = 20,
        source: Optional[str] = None,
        sentiment: Optional[str] = None,
        topic: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        search_text: Optional[str] = None,
    ):
        # =========================================================
        # Validate pagination
        # =========================================================

        page = max(page, 1)

        page_size = min(
            max(page_size, 1),
            100,
        )

        # =========================================================
        # Find selected search
        # =========================================================

        selected_search = (
            db.query(Search)
            .filter(
                Search.id == search_id
            )
            .first()
        )

        if selected_search is None:
            return None

        # =========================================================
        # Determine active keyword
        # =========================================================

        keyword = (
            selected_search.keyword or ""
        ).strip()

        if not keyword:
            return {
                "items": [],
                "total": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 0,
            }

        normalized_keyword = keyword.lower()

        # =========================================================
        # Base query
        #
        # IMPORTANT:
        #
        # We intentionally do NOT use:
        #
        #     Mention.search_id == search_id
        #
        # because scheduled monitoring creates a new Search row
        # on every run.
        #
        # Instead, we retrieve mentions belonging to searches with
        # the same keyword.
        # =========================================================

        query = (
            db.query(
                Mention,
                MentionAnalysis,
            )
            .join(
                MentionAnalysis,
                Mention.id
                == MentionAnalysis.mention_id,
            )
            .join(
                Search,
                Mention.search_id
                == Search.id,
            )
            .filter(
                func.lower(
                    func.trim(Search.keyword)
                )
                == normalized_keyword
            )
            .filter(
                Search.status == "completed"
            )
            .filter(
                MentionAnalysis.is_relevant.is_(True)
            )
            .filter(
                MentionAnalysis.is_duplicate.is_(False)
            )
        )

        # =========================================================
        # Source filter
        # =========================================================

        if source:
            query = query.filter(
                Mention.source == source
            )

        # =========================================================
        # Sentiment filter
        # =========================================================

        if sentiment:
            query = query.filter(
                MentionAnalysis.sentiment
                == sentiment
            )

        # =========================================================
        # Topic filter
        # =========================================================

        if topic:
            query = query.filter(
                MentionAnalysis.topic
                == topic
            )

        # =========================================================
        # Start date filter
        #
        # Prefer published_at.
        # If published_at is unavailable, collected_at is used.
        # =========================================================

        if start_date:
            query = query.filter(
                or_(
                    Mention.published_at
                    >= start_date,

                    (
                        Mention.published_at.is_(None)
                        &
                        (
                            Mention.collected_at
                            >= start_date
                        )
                    ),
                )
            )

        # =========================================================
        # End date filter
        # =========================================================

        if end_date:
            query = query.filter(
                or_(
                    Mention.published_at
                    <= end_date,

                    (
                        Mention.published_at.is_(None)
                        &
                        (
                            Mention.collected_at
                            <= end_date
                        )
                    ),
                )
            )

        # =========================================================
        # Text search
        # =========================================================

        if search_text:
            search_value = (
                search_text.strip()
            )

            if search_value:
                search_pattern = (
                    f"%{search_value}%"
                )

                query = query.filter(
                    or_(
                        Mention.title.ilike(
                            search_pattern
                        ),
                        Mention.content.ilike(
                            search_pattern
                        ),
                    )
                )

        # =========================================================
        # Fetch all matching rows before cross-search deduplication
        #
        # Scheduled monitoring can collect the same external article
        # more than once in different Search records.
        #
        # We remove those repeated copies below.
        # =========================================================

        rows = (
            query
            .order_by(
                Mention.collected_at.desc(),
                Mention.id.desc(),
            )
            .all()
        )

        # =========================================================
        # Cross-search deduplication
        #
        # Priority:
        #
        # 1. source + source_id
        # 2. source + URL
        # 3. unique database mention ID
        #
        # This prevents the same article/question/story from appearing
        # repeatedly when scheduled monitoring runs again.
        # =========================================================

        unique_rows = []

        seen_keys = set()

        for mention, analysis in rows:

            source_name = (
                mention.source or ""
            ).strip().lower()

            source_id = (
                mention.source_id or ""
            ).strip()

            url = (
                mention.url or ""
            ).strip().lower()

            if source_id:
                dedupe_key = (
                    "source_id",
                    source_name,
                    source_id,
                )

            elif url:
                dedupe_key = (
                    "url",
                    source_name,
                    url,
                )

            else:
                dedupe_key = (
                    "mention_id",
                    mention.id,
                )

            if dedupe_key in seen_keys:
                continue

            seen_keys.add(
                dedupe_key
            )

            unique_rows.append(
                (
                    mention,
                    analysis,
                )
            )

        # =========================================================
        # Sort final unique results
        #
        # Published date is preferred.
        # Collected date is the fallback.
        # =========================================================

        def sort_datetime(row):
            mention = row[0]

            return (
                mention.published_at
                or mention.collected_at
                or datetime.min
            )

        unique_rows.sort(
            key=sort_datetime,
            reverse=True,
        )

        # =========================================================
        # Count
        # =========================================================

        total = len(
            unique_rows
        )

        # =========================================================
        # Calculate pagination
        # =========================================================

        total_pages = (
            ceil(
                total / page_size
            )
            if total > 0
            else 0
        )

        offset = (
            (page - 1)
            * page_size
        )

        page_rows = unique_rows[
            offset:
            offset + page_size
        ]

        # =========================================================
        # Convert database rows
        # =========================================================

        items = []

        for mention, analysis in page_rows:

            items.append(
                {
                    "id": mention.id,

                    "source": mention.source,

                    "source_id": (
                        mention.source_id
                    ),

                    "url": mention.url,

                    "title": mention.title,

                    "content": mention.content,

                    "author": mention.author,

                    "published_at": (
                        mention.published_at
                    ),

                    "keyword": mention.keyword,

                    "engagement": (
                        mention.engagement
                    ),

                    "relevance_score": (
                        analysis.relevance_score
                    ),

                    "sentiment": (
                        analysis.sentiment
                    ),

                    "sentiment_confidence": (
                        analysis.sentiment_confidence
                    ),

                    "topic": (
                        analysis.topic
                    ),

                    "topic_confidence": (
                        analysis.topic_confidence
                    ),

                    "collected_at": (
                        mention.collected_at
                    ),
                }
            )

        # =========================================================
        # Return paginated response
        # =========================================================

        return {
            "items": items,

            "total": total,

            "page": page,

            "page_size": page_size,

            "total_pages": total_pages,
        }