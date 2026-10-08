from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class CollectedMention:
    source: str
    source_id: Optional[str]
    url: str
    title: Optional[str]
    content: str
    author: Optional[str]
    published_at: Optional[datetime]
    keyword: str
    engagement: int = 0