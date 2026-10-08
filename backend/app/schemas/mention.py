from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class MentionResponse(BaseModel):
    id: int

    source: str
    source_id: Optional[str] = None

    url: str
    title: Optional[str] = None
    content: str

    author: Optional[str] = None
    published_at: Optional[datetime] = None

    keyword: str
    engagement: int

    relevance_score: Optional[float] = None
    sentiment: Optional[str] = None
    sentiment_confidence: Optional[float] = None

    topic: Optional[str] = None
    topic_confidence: Optional[float] = None

    collected_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class MentionListResponse(BaseModel):
    items: list[MentionResponse]

    total: int
    page: int
    page_size: int
    total_pages: int