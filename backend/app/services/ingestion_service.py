from typing import List

from app.collectors.base import BaseCollector
from app.collectors.models import CollectedMention


class IngestionService:
    """
    Coordinates data collection from multiple sources.

    Each collector is responsible for communicating with its own
    external source. This service coordinates them and returns a
    combined collection of mentions.
    """

    def __init__(self, collectors: List[BaseCollector]):
        self.collectors = collectors

    def collect(
        self,
        keyword: str,
        limit_per_source: int = 50,
    ) -> List[CollectedMention]:
        """
        Collect mentions from all configured sources.

        Args:
            keyword: Brand, product, company, or keyword to search.
            limit_per_source: Maximum mentions collected from each source.

        Returns:
            Combined list of collected mentions.
        """

        all_mentions: List[CollectedMention] = []

        for collector in self.collectors:
            print(
                f"\nStarting collector: "
                f"{collector.source_name}"
            )

            mentions = collector.collect(
                keyword=keyword,
                limit=limit_per_source,
            )

            print(
                f"Finished collector: "
                f"{collector.source_name} "
                f"({len(mentions)} mentions)"
            )

            all_mentions.extend(mentions)

        return all_mentions