from datetime import datetime, timezone

from app.collectors.models import CollectedMention
from app.services.deduplication_service import (
    DeduplicationService,
)
from app.services.normalization_service import (
    NormalizationService,
)
from app.services.relevance_service import (
    RelevanceService,
)
from app.services.sentiment_service import (
    SentimentService,
)
from app.services.topic_service import (
    TopicService,
)


class ProcessedMention:

    def __init__(
        self,
        mention,
        relevance_score,
        is_relevant,
    ):
        self.mention = mention

        self.relevance_score = (
            relevance_score
        )

        self.is_relevant = (
            is_relevant
        )

        self.is_duplicate = False

        self.duplicate_of = None

        self.sentiment = None

        self.sentiment_confidence = None

        self.topic = None

        self.topic_confidence = None

        self.processed_at = (
            datetime.now(timezone.utc)
        )


class ProcessingService:

    def __init__(
        self,
        normalization_service=None,
        relevance_service=None,
        deduplication_service=None,
        sentiment_service=None,
        topic_service=None,
    ):

        self.normalization_service = (
            normalization_service
            or NormalizationService()
        )

        self.relevance_service = (
            relevance_service
            or RelevanceService()
        )

        self.deduplication_service = (
            deduplication_service
            or DeduplicationService()
        )

        self.sentiment_service = (
            sentiment_service
            or SentimentService()
        )

        self.topic_service = (
            topic_service
            or TopicService()
        )

    # ==================================================
    # MAIN PROCESSING PIPELINE
    # ==================================================

    def process(
        self,
        mentions: list[CollectedMention],
    ):

        processed_mentions = []

        # Only normalized mentions that survive
        # relevance filtering are considered for
        # duplicate comparison.
        unique_relevant_mentions = []

        for mention in mentions:

            # ------------------------------------------
            # 1. NORMALIZATION
            # ------------------------------------------

            normalized = (
                self.normalization_service.normalize(
                    mention
                )
            )

            if normalized is None:
                continue

            # ------------------------------------------
            # 2. RELEVANCE
            # ------------------------------------------

            (
                relevance_score,
                is_relevant,
            ) = self.relevance_service.analyze(
                normalized
            )

            processed = ProcessedMention(
                mention=normalized,
                relevance_score=relevance_score,
                is_relevant=is_relevant,
            )

            # ------------------------------------------
            # 3. DEDUPLICATION
            # ------------------------------------------

            if is_relevant:

                duplicate_index = (
                    self.deduplication_service.find_duplicate(
                        normalized,
                        unique_relevant_mentions,
                    )
                )

                if duplicate_index is not None:

                    processed.is_duplicate = True

                    processed.duplicate_of = (
                        duplicate_index + 1
                    )

                else:

                    unique_relevant_mentions.append(
                        normalized
                    )

            # ------------------------------------------
            # 4. NLP ANALYSIS
            # ------------------------------------------

            if (
                processed.is_relevant
                and not processed.is_duplicate
            ):

                analysis_text = (
                    f"{normalized.title or ''}. "
                    f"{normalized.content or ''}"
                ).strip()

                # Sentiment
                sentiment_result = (
                    self.sentiment_service.analyze(
                        analysis_text
                    )
                )

                processed.sentiment = (
                    sentiment_result[
                        "sentiment"
                    ]
                )

                processed.sentiment_confidence = (
                    sentiment_result[
                        "confidence"
                    ]
                )

                # Topic
                topic_result = (
                    self.topic_service.analyze(
                        analysis_text
                    )
                )

                processed.topic = (
                    topic_result["topic"]
                )

                processed.topic_confidence = (
                    topic_result[
                        "confidence"
                    ]
                )

            processed_mentions.append(
                processed
            )

        return processed_mentions

    # ==================================================
    # RELEVANT MENTIONS
    # ==================================================

    @staticmethod
    def get_relevant_mentions(
        processed_mentions,
    ):

        return [
            processed
            for processed in processed_mentions
            if (
                processed.is_relevant
                and not processed.is_duplicate
            )
        ]

    # ==================================================
    # STATISTICS
    # ==================================================

    @staticmethod
    def get_processing_statistics(
        processed_mentions,
    ):

        total = len(
            processed_mentions
        )

        relevant = sum(
            1
            for item in processed_mentions
            if item.is_relevant
        )

        irrelevant = sum(
            1
            for item in processed_mentions
            if not item.is_relevant
        )

        duplicates = sum(
            1
            for item in processed_mentions
            if item.is_duplicate
        )

        unique_relevant = sum(
            1
            for item in processed_mentions
            if (
                item.is_relevant
                and not item.is_duplicate
            )
        )

        return {
            "total": total,
            "relevant": relevant,
            "irrelevant": irrelevant,
            "duplicates": duplicates,
            "unique_relevant": unique_relevant,
        }