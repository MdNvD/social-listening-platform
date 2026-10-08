from app.collectors.hackernews import HackerNewsCollector
from app.collectors.rss import RSSCollector
from app.collectors.stackexchange import (
    StackExchangeCollector,
)

from app.services.ingestion_service import (
    IngestionService,
)

from app.services.processing_service import (
    ProcessingService,
)


class SearchService:
    """
    Coordinates the complete social listening search pipeline.

    Flow:

        Collect
            ↓
        Normalize
            ↓
        Relevance filtering
            ↓
        Deduplication
            ↓
        Sentiment
            ↓
        Topic classification
    """

    RSS_FEEDS = [
        "https://techcrunch.com/feed/",
        "https://www.theverge.com/rss/index.xml",
        "https://feeds.arstechnica.com/arstechnica/index",
        "http://feed.androidauthority.com/",
    ]

    def __init__(self):

        self.processing_service = (
            ProcessingService()
        )

    # ==================================================
    # RUN SEARCH
    # ==================================================

    def run_search(
        self,
        keyword: str,
        limit_per_source: int = 50,
    ):

        keyword = keyword.strip()

        if not keyword:
            raise ValueError(
                "Keyword cannot be empty."
            )

        # ------------------------------------------
        # CREATE COLLECTORS
        # ------------------------------------------

        collectors = (
            self._create_collectors()
        )

        # ------------------------------------------
        # INGESTION
        # ------------------------------------------

        ingestion_service = (
            IngestionService(
                collectors=collectors
            )
        )

        raw_mentions = (
            ingestion_service.collect(
                keyword=keyword,
                limit_per_source=limit_per_source,
            )
        )

        print(
            f"\nTotal raw mentions collected: "
            f"{len(raw_mentions)}"
        )

        # ------------------------------------------
        # PROCESSING
        # ------------------------------------------

        processed_mentions = (
            self.processing_service.process(
                raw_mentions
            )
        )

        # ------------------------------------------
        # RELEVANT MENTIONS
        # ------------------------------------------

        relevant_mentions = (
            self.processing_service
            .get_relevant_mentions(
                processed_mentions
            )
        )

        # ------------------------------------------
        # STATISTICS
        # ------------------------------------------

        statistics = (
            self.processing_service
            .get_processing_statistics(
                processed_mentions
            )
        )

        # ------------------------------------------
        # RETURN RESULT
        # ------------------------------------------

        return {
            "keyword": keyword,
            "raw_mentions": raw_mentions,
            "processed_mentions": processed_mentions,
            "relevant_mentions": relevant_mentions,
            "statistics": statistics,
        }

    # ==================================================
    # CREATE COLLECTORS
    # ==================================================

    @classmethod
    def _create_collectors(cls):

        # ------------------------------------------
        # RSS
        # ------------------------------------------

        rss_collector = (
            RSSCollector(
                feed_urls=cls.RSS_FEEDS
            )
        )

        # ------------------------------------------
        # HACKER NEWS
        # ------------------------------------------

        hackernews_collector = (
            HackerNewsCollector()
        )

        # ------------------------------------------
        # STACK EXCHANGE
        # ------------------------------------------

        stackexchange_collector = (
            StackExchangeCollector()
        )

        # ------------------------------------------
        # RETURN ALL COLLECTORS
        # ------------------------------------------

        return [
            rss_collector,
            hackernews_collector,
            stackexchange_collector,
        ]