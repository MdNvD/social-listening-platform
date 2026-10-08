from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SentimentCount(BaseModel):
    sentiment: str
    count: int


class TopicCount(BaseModel):
    topic: str
    count: int


class SourceCount(BaseModel):
    source: str
    count: int


class MentionTrendPoint(BaseModel):
    date: str
    count: int


class AnalyticsResponse(BaseModel):
    search_id: int
    keyword: str

    total_collected: int
    total_processed: int

    total_mentions: int

    sentiment_distribution: list[
        SentimentCount
    ]

    topic_distribution: list[
        TopicCount
    ]

    source_distribution: list[
        SourceCount
    ]

    mentions_over_time: list[
        MentionTrendPoint
    ]

    first_mention_at: Optional[datetime] = None

    last_mention_at: Optional[datetime] = None