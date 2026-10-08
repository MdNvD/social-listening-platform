from abc import ABC, abstractmethod
from typing import List

from app.collectors.models import CollectedMention


class BaseCollector(ABC):
    """
    Base interface for all social listening data collectors.
    """

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Return the name of the data source."""
        raise NotImplementedError

    @abstractmethod
    def collect(
        self,
        keyword: str,
        limit: int = 50,
    ) -> List[CollectedMention]:
        """
        Collect public mentions for a keyword.
        """
        raise NotImplementedError