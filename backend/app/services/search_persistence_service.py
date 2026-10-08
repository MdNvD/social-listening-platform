from datetime import datetime, timezone
from typing import List

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.database.models import Mention, MentionAnalysis, Search
from app.services.processing_service import ProcessedMention


class SearchPersistenceService:
    """
    Persists search results and processed mentions into PostgreSQL.

    Flow:

        Search
          ↓
        Processed mentions
          ↓
        Cross-search duplicate check
          ↓
        Search record updated
          ↓
        Mentions saved
          ↓
        Mention analysis saved
              ↓
        Relevance
        Sentiment
        Topic
        Confidence scores
    """

    def save_search_results(
        self,
        db: Session,
        search: Search,
        processed_mentions: List[ProcessedMention],
        raw_count: int,
    ) -> int:
        """
        Save processed mentions belonging to a search.

        Only relevant, non-duplicate mentions are persisted as
        usable social-listening data.

        In addition to the normal processing-time deduplication,
        this method performs a database-level cross-search
        duplicate check.

        A mention is considered an existing cross-search duplicate
        when it has:

            Same source
            + Same keyword (case-insensitive)
            + Same source_id

        or, when source_id is unavailable:

            Same source
            + Same keyword (case-insensitive)
            + Same URL

        This allows the same public item to legitimately appear
        under different searches/keywords while preventing repeated
        scheduled runs from storing the same item repeatedly.

        Args:
            db:
                Database session.

            search:
                Search record being processed.

            processed_mentions:
                Mentions after normalization, relevance checking,
                deduplication, sentiment analysis, and topic analysis.

            raw_count:
                Number of mentions originally returned by the
                collectors before processing.

        Returns:
            Number of newly saved unique relevant mentions.
        """

        saved_count = 0

        for processed in processed_mentions:

            # ---------------------------------------------------------
            # IGNORE IRRELEVANT MENTIONS
            # ---------------------------------------------------------

            if not processed.is_relevant:
                continue

            # ---------------------------------------------------------
            # IGNORE WITHIN-SEARCH DUPLICATES
            # ---------------------------------------------------------

            if processed.is_duplicate:
                continue

            mention_data = processed.mention

            # ---------------------------------------------------------
            # NORMALIZE KEYWORD FOR CROSS-SEARCH COMPARISON
            # ---------------------------------------------------------

            normalized_keyword = (
                mention_data.keyword.strip()
                if mention_data.keyword
                else ""
            )

            # ---------------------------------------------------------
            # CROSS-SEARCH DUPLICATE CHECK
            # ---------------------------------------------------------
            #
            # Scheduled monitoring can collect the same public item
            # repeatedly.
            #
            # We therefore check the database before inserting.
            #
            # IMPORTANT:
            #
            # The keyword is included in the identity.
            #
            # This means:
            #
            #   Samsung Galaxy S26 + Hacker News + 12345
            #
            # and:
            #
            #   Google Pixel + Hacker News + 12345
            #
            # can both exist if they are relevant to their respective
            # searches.
            #
            # Keyword comparison is case-insensitive through ilike().
            # ---------------------------------------------------------

            duplicate_query = None

            # ---------------------------------------------------------
            # METHOD 1: SOURCE + KEYWORD + SOURCE_ID
            # ---------------------------------------------------------

            if mention_data.source_id:

                duplicate_query = (
                    db.query(Mention)
                    .filter(
                        and_(
                            Mention.source == mention_data.source,
                            Mention.source_id == mention_data.source_id,
                            Mention.keyword.ilike(
                                normalized_keyword
                            ),
                        )
                    )
                    .first()
                )

            # ---------------------------------------------------------
            # METHOD 2: SOURCE + KEYWORD + URL
            # ---------------------------------------------------------
            #
            # Used when source_id is unavailable or when source_id
            # did not identify an existing record.
            # ---------------------------------------------------------

            if duplicate_query is None and mention_data.url:

                duplicate_query = (
                    db.query(Mention)
                    .filter(
                        and_(
                            Mention.source == mention_data.source,
                            Mention.url == mention_data.url,
                            Mention.keyword.ilike(
                                normalized_keyword
                            ),
                        )
                    )
                    .first()
                )

            # ---------------------------------------------------------
            # SKIP EXISTING CROSS-SEARCH DUPLICATE
            # ---------------------------------------------------------

            if duplicate_query is not None:
                continue

            # ---------------------------------------------------------
            # SAVE MENTION
            # ---------------------------------------------------------

            mention = Mention(
                search_id=search.id,
                source=mention_data.source,
                source_id=mention_data.source_id,
                url=mention_data.url,
                title=mention_data.title,
                content=mention_data.content,
                author=mention_data.author,
                published_at=mention_data.published_at,
                keyword=mention_data.keyword,
                engagement=mention_data.engagement,
            )

            db.add(mention)

            # Flush so PostgreSQL generates mention.id.
            db.flush()

            # ---------------------------------------------------------
            # SAVE ANALYSIS
            # ---------------------------------------------------------

            analysis = MentionAnalysis(
                mention_id=mention.id,

                # Relevance
                relevance_score=processed.relevance_score,
                is_relevant=processed.is_relevant,

                # Duplicate information
                is_duplicate=processed.is_duplicate,
                duplicate_of=processed.duplicate_of,

                # Sentiment
                sentiment=processed.sentiment,
                sentiment_confidence=processed.sentiment_confidence,

                # Topic
                topic=processed.topic,
                topic_confidence=processed.topic_confidence,

                # Processing timestamp
                processed_at=processed.processed_at,
            )

            db.add(analysis)

            saved_count += 1

        # -------------------------------------------------------------
        # UPDATE SEARCH STATISTICS
        # -------------------------------------------------------------

        # Number returned directly by the collectors.
        search.total_collected = raw_count

        # Number of newly saved relevant and unique mentions.
        #
        # This excludes:
        #
        #   1. Irrelevant mentions
        #   2. Within-search duplicates
        #   3. Cross-search duplicates
        #
        # Therefore this represents NEW mentions actually inserted
        # into the database for this search.
        search.total_processed = saved_count

        # -------------------------------------------------------------
        # COMMIT
        # -------------------------------------------------------------

        db.commit()

        return saved_count

    @staticmethod
    def mark_search_started(
        db: Session,
        search: Search,
    ) -> None:
        """
        Mark a search as running.
        """

        search.status = "running"
        search.started_at = datetime.now(timezone.utc)

        db.commit()

    @staticmethod
    def mark_search_completed(
        db: Session,
        search: Search,
    ) -> None:
        """
        Mark a search as successfully completed.
        """

        search.status = "completed"
        search.completed_at = datetime.now(timezone.utc)

        db.commit()

    @staticmethod
    def mark_search_failed(
        db: Session,
        search: Search,
    ) -> None:
        """
        Mark a search as failed.
        """

        search.status = "failed"
        search.completed_at = datetime.now(timezone.utc)

        db.commit()