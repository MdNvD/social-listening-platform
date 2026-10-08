from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SearchCreate(BaseModel):
    keyword: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Brand, product, company, or keyword to monitor",
    )


class SearchResponse(BaseModel):
    id: int
    keyword: str
    status: str
    created_at: datetime
    total_collected: int
    total_processed: int

    model_config = ConfigDict(from_attributes=True)