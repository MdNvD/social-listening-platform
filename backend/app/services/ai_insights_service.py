from collections import Counter
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.models import (
    Mention,
    MentionAnalysis,
    Search,
)

from app.services.llm_service import LLMService


class AIInsightsService:
    """
    Builds structured evidence for AI-generated insights.

    Evidence is collected at the KEYWORD level rather than
    only from one Search record.

    Scheduled monitoring creates multiple Search records for
    the same keyword.

    Example:

        Search #78  -> Samsung Galaxy S26
        Search #104 -> Samsung Galaxy S26
        Search #111 -> Samsung Galaxy S26

    AI Insights therefore analyzes accumulated unique evidence
    for the keyword.
    """

    MAX_EVIDENCE_MENTIONS = 20

    MAX_SEARCHES = 100

    def __init__(self):
        self.llm_service = LLMService()

    # =========================================================
    # Build deterministic evidence
    # =========================================================

    def build_evidence(
        self,
        db: Session,
        search_id: int,
    ) -> dict[str, Any]:

        # -----------------------------------------------------
        # Resolve selected search
        # -----------------------------------------------------

        selected_search = (
            db.query(Search)
            .filter(
                Search.id == search_id,
            )
            .first()
        )

        if selected_search is None:
            return self._empty_evidence(
                search_id=search_id,
                keyword=None,
            )

        # -----------------------------------------------------
        # Resolve keyword
        # -----------------------------------------------------

        keyword = (
            selected_search.keyword
            or ""
        ).strip()

        if not keyword:
            return self._empty_evidence(
                search_id=search_id,
                keyword=None,
            )

        # =====================================================
        # Find completed searches for keyword
        # =====================================================

        completed_searches = (
            db.query(Search.id)
            .filter(
                func.lower(
                    func.trim(Search.keyword)
                ) == keyword.lower(),

                Search.status == "completed",
            )
            .order_by(
                Search.completed_at.desc(),
                Search.id.desc(),
            )
            .limit(
                self.MAX_SEARCHES
            )
            .all()
        )

        search_ids = [
            row[0]
            for row in completed_searches
        ]

        # -----------------------------------------------------
        # Make sure selected search is included
        # -----------------------------------------------------

        if (
            selected_search.status == "completed"
            and search_id not in search_ids
        ):
            search_ids.append(
                search_id
            )

        if not search_ids:
            return self._empty_evidence(
                search_id=search_id,
                keyword=keyword,
            )

        # =====================================================
        # Load analyzed mentions
        # =====================================================

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
                Mention.search_id.in_(
                    search_ids
                ),

                MentionAnalysis.is_relevant.is_(
                    True
                ),

                MentionAnalysis.is_duplicate.is_(
                    False
                ),
            )
            .all()
        )

        # =====================================================
        # Cross-search deduplication
        # =====================================================

        unique_rows = self._deduplicate_rows(
            rows
        )

        # -----------------------------------------------------
        # No usable evidence
        # -----------------------------------------------------

        if not unique_rows:
            return self._empty_evidence(
                search_id=search_id,
                keyword=keyword,
                search_ids=search_ids,
            )

        # =====================================================
        # Source distribution
        # =====================================================

        source_counter = Counter()

        for mention, analysis in unique_rows:

            if mention.source:
                source_counter[
                    mention.source
                ] += 1

        source_distribution = [
            {
                "source": source,
                "count": count,
            }
            for source, count in sorted(
                source_counter.items(),
                key=lambda item: (
                    -item[1],
                    item[0],
                ),
            )
        ]

        # =====================================================
        # Sentiment distribution
        # =====================================================

        sentiment_counter = Counter()

        for mention, analysis in unique_rows:

            sentiment = (
                analysis.sentiment
                or "neutral"
            )

            sentiment_counter[
                sentiment
            ] += 1

        sentiment_distribution = [
            {
                "sentiment": sentiment,
                "count": count,
            }
            for sentiment, count in sorted(
                sentiment_counter.items(),
                key=lambda item: (
                    -item[1],
                    item[0],
                ),
            )
        ]

        # =====================================================
        # Topic distribution
        # =====================================================

        topic_counter = Counter()

        for mention, analysis in unique_rows:

            topic = (
                analysis.topic
                or "Other"
            )

            topic_counter[
                topic
            ] += 1

        topic_distribution = [
            {
                "topic": topic,
                "count": count,
            }
            for topic, count in sorted(
                topic_counter.items(),
                key=lambda item: (
                    -item[1],
                    item[0],
                ),
            )
        ]

        # =====================================================
        # Representative mentions
        # =====================================================

        representative_rows = sorted(
            unique_rows,
            key=lambda row: (
                self._representative_score(
                    row[0],
                    row[1],
                )
            ),
            reverse=True,
        )

        representative_mentions = [
            self._mention_to_dict(
                mention,
                analysis,
            )
            for mention, analysis
            in representative_rows[
                : self.MAX_EVIDENCE_MENTIONS
            ]
        ]

        # =====================================================
        # Positive observations
        # =====================================================

        positive_rows = [
            (
                mention,
                analysis,
            )
            for mention, analysis in unique_rows
            if analysis.sentiment == "positive"
        ]

        positive_rows.sort(
            key=lambda row: (
                row[1].sentiment_confidence
                or 0.0
            ),
            reverse=True,
        )

        positive_observations = [
            self._mention_to_dict(
                mention,
                analysis,
            )
            for mention, analysis
            in positive_rows[:5]
        ]

        # =====================================================
        # Negative observations
        # =====================================================

        negative_rows = [
            (
                mention,
                analysis,
            )
            for mention, analysis in unique_rows
            if analysis.sentiment == "negative"
        ]

        negative_rows.sort(
            key=lambda row: (
                row[1].sentiment_confidence
                or 0.0
            ),
            reverse=True,
        )

        negative_observations = [
            self._mention_to_dict(
                mention,
                analysis,
            )
            for mention, analysis
            in negative_rows[:5]
        ]

        # -----------------------------------------------------
        # Total negative mentions
        # -----------------------------------------------------

        negative_mention_count = len(
            negative_rows
        )

        # =====================================================
        # Potential pain points
        # =====================================================

        pain_point_topics = {
            "Complaints",
            "Quality",
            "Customer service",
        }

        pain_point_rows = [
            (
                mention,
                analysis,
            )
            for mention, analysis in unique_rows
            if (
                analysis.sentiment == "negative"
                or analysis.topic
                in pain_point_topics
            )
        ]

        pain_point_rows.sort(
            key=lambda row: (
                self._pain_point_score(
                    row[0],
                    row[1],
                )
            ),
            reverse=True,
        )

        potential_pain_points = [
            self._mention_to_dict(
                mention,
                analysis,
            )
            for mention, analysis
            in pain_point_rows[:5]
        ]

        # =====================================================
        # Potential opportunities
        # =====================================================

        opportunity_topics = {
            "Features",
            "Product",
            "Pricing",
        }

        opportunity_rows = [
            (
                mention,
                analysis,
            )
            for mention, analysis in unique_rows
            if (
                analysis.topic
                in opportunity_topics
                or analysis.sentiment == "positive"
            )
        ]

        opportunity_rows.sort(
            key=lambda row: (
                self._representative_score(
                    row[0],
                    row[1],
                )
            ),
            reverse=True,
        )

        potential_opportunities = [
            self._mention_to_dict(
                mention,
                analysis,
            )
            for mention, analysis
            in opportunity_rows[:5]
        ]

        # =====================================================
        # Return evidence package
        # =====================================================

        return {
            "search_id": search_id,

            "keyword": keyword,

            "search_count": len(
                search_ids
            ),

            "search_ids": search_ids,

            "total_mentions": len(
                unique_rows
            ),

            "negative_mention_count": (
                negative_mention_count
            ),

            "source_distribution": (
                source_distribution
            ),

            "sentiment_distribution": (
                sentiment_distribution
            ),

            "topic_distribution": (
                topic_distribution
            ),

            "representative_mentions": (
                representative_mentions
            ),

            "positive_observations": (
                positive_observations
            ),

            "negative_observations": (
                negative_observations
            ),

            "potential_pain_points": (
                potential_pain_points
            ),

            "potential_opportunities": (
                potential_opportunities
            ),
        }

    # =========================================================
    # Cross-search deduplication
    # =========================================================

    @staticmethod
    def _deduplicate_rows(
        rows,
    ):
        """
        Remove the same external mention appearing in multiple
        scheduled Search records.

        Priority:

            1. URL
            2. source + source_id
            3. normalized title + content

        This changes only the AI evidence calculation.

        It does NOT delete database records.
        """

        unique_rows = []

        seen_urls = set()
        seen_source_ids = set()
        seen_text = set()

        for mention, analysis in rows:

            # -------------------------------------------------
            # URL
            # -------------------------------------------------

            url = (
                mention.url or ""
            ).strip().lower()

            normalized_url = None

            if url:
                normalized_url = (
                    url.rstrip("/")
                )

                if (
                    normalized_url
                    in seen_urls
                ):
                    continue

            # -------------------------------------------------
            # Source + source ID
            # -------------------------------------------------

            source = (
                mention.source or ""
            ).strip().lower()

            source_id = (
                mention.source_id or ""
            ).strip().lower()

            source_key = None

            if source and source_id:

                source_key = (
                    source,
                    source_id,
                )

                if (
                    source_key
                    in seen_source_ids
                ):
                    continue

            # -------------------------------------------------
            # Normalized text
            # -------------------------------------------------

            title = (
                mention.title or ""
            ).strip().lower()

            content = (
                mention.content or ""
            ).strip().lower()

            normalized_text = " ".join(
                f"{title} {content}".split()
            )

            text_key = (
                source,
                normalized_text,
            )

            if normalized_text:

                if (
                    text_key
                    in seen_text
                ):
                    continue

            # -------------------------------------------------
            # Mark seen
            # -------------------------------------------------

            if normalized_url:
                seen_urls.add(
                    normalized_url
                )

            if source_key:
                seen_source_ids.add(
                    source_key
                )

            if normalized_text:
                seen_text.add(
                    text_key
                )

            unique_rows.append(
                (
                    mention,
                    analysis,
                )
            )

        return unique_rows

    # =========================================================
    # Empty evidence
    # =========================================================

    @staticmethod
    def _empty_evidence(
        search_id: int,
        keyword: str | None,
        search_ids=None,
    ) -> dict[str, Any]:

        return {
            "search_id": search_id,

            "keyword": keyword,

            "search_count": len(
                search_ids or []
            ),

            "search_ids": (
                search_ids or []
            ),

            "total_mentions": 0,

            "negative_mention_count": 0,

            "source_distribution": [],

            "sentiment_distribution": [],

            "topic_distribution": [],

            "representative_mentions": [],

            "positive_observations": [],

            "negative_observations": [],

            "potential_pain_points": [],

            "potential_opportunities": [],
        }

    # =========================================================
    # Generate AI insights
    # =========================================================

    def generate_ai_insights(
        self,
        keyword: str,
        evidence: dict[str, Any],
    ) -> dict[str, Any]:

        total_mentions = int(
            evidence.get(
                "total_mentions",
                0,
            )
            or 0
        )

        if total_mentions <= 0:

            return {
                "summary": (
                    "There is not enough collected evidence "
                    f"to generate meaningful AI insights for "
                    f"{keyword}."
                ),

                "key_themes": [],

                "pain_points": [],

                "opportunities": [],

                "recommended_actions": [
                    "Collect additional mentions before "
                    "drawing broader conclusions."
                ],

                "limitations": [
                    "No relevant, non-duplicate mentions "
                    "were available for this keyword."
                ],
            }

        return self.llm_service.generate_insights(
            keyword=keyword,
            evidence=evidence,
        )

    # =========================================================
    # Complete insight package
    # =========================================================

    def build_complete_insights(
        self,
        db: Session,
        search_id: int,
        keyword: str,
    ) -> dict[str, Any]:

        selected_search = (
            db.query(Search)
            .filter(
                Search.id == search_id,
            )
            .first()
        )

        if selected_search is None:

            evidence = self._empty_evidence(
                search_id=search_id,
                keyword=keyword,
            )

            ai_insights = self.generate_ai_insights(
                keyword=keyword,
                evidence=evidence,
            )

            return {
                "keyword": keyword,
                "evidence": evidence,
                "ai_insights": ai_insights,
            }

        # -----------------------------------------------------
        # Database keyword is authoritative
        # -----------------------------------------------------

        resolved_keyword = (
            selected_search.keyword
            or keyword
            or ""
        ).strip()

        # -----------------------------------------------------
        # Build accumulated evidence
        # -----------------------------------------------------

        evidence = self.build_evidence(
            db=db,
            search_id=search_id,
        )

        # -----------------------------------------------------
        # Generate AI insights
        # -----------------------------------------------------

        ai_insights = self.generate_ai_insights(
            keyword=resolved_keyword,
            evidence=evidence,
        )

        return {
            "keyword": resolved_keyword,

            "evidence": evidence,

            "ai_insights": ai_insights,
        }

    # =========================================================
    # Representative score
    # =========================================================

    @staticmethod
    def _representative_score(
        mention: Mention,
        analysis: MentionAnalysis,
    ) -> float:

        relevance = (
            analysis.relevance_score
            or 0.0
        )

        sentiment_confidence = (
            analysis.sentiment_confidence
            or 0.0
        )

        topic_confidence = (
            analysis.topic_confidence
            or 0.0
        )

        engagement = (
            mention.engagement
            or 0
        )

        engagement_signal = min(
            engagement / 100.0,
            1.0,
        )

        return (
            relevance * 0.40
            + sentiment_confidence * 0.20
            + topic_confidence * 0.20
            + engagement_signal * 0.20
        )

    # =========================================================
    # Pain point score
    # =========================================================

    @staticmethod
    def _pain_point_score(
        mention: Mention,
        analysis: MentionAnalysis,
    ) -> float:

        negative_signal = (
            1.0
            if analysis.sentiment == "negative"
            else 0.0
        )

        topic_signal = (
            1.0
            if analysis.topic
            in {
                "Complaints",
                "Quality",
                "Customer service",
            }
            else 0.0
        )

        sentiment_confidence = (
            analysis.sentiment_confidence
            or 0.0
        )

        topic_confidence = (
            analysis.topic_confidence
            or 0.0
        )

        return (
            negative_signal * 0.40
            + topic_signal * 0.30
            + sentiment_confidence * 0.15
            + topic_confidence * 0.15
        )

    # =========================================================
    # Mention → evidence dictionary
    # =========================================================

    @staticmethod
    def _mention_to_dict(
        mention: Mention,
        analysis: MentionAnalysis,
    ) -> dict[str, Any]:

        return {
            "id": mention.id,

            "source": mention.source,

            "url": mention.url,

            "title": mention.title,

            "content": mention.content,

            "author": mention.author,

            "published_at": (
                mention.published_at
            ),

            "collected_at": (
                mention.collected_at
            ),

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
        }