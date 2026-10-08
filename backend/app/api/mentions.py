from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.mention import MentionListResponse
from app.services.mention_service import MentionService


router = APIRouter(
    prefix="/api/searches",
    tags=["Mentions"],
)


@router.get(
    "/{search_id}/mentions",
    response_model=MentionListResponse,
)
def get_search_mentions(
    search_id: int,

    page: int = Query(
        default=1,
        ge=1,
        description="Page number",
    ),

    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Number of mentions per page",
    ),

    source: Optional[str] = Query(
        default=None,
        description="Filter by source",
    ),

    sentiment: Optional[str] = Query(
        default=None,
        description="Filter by sentiment",
    ),

    topic: Optional[str] = Query(
        default=None,
        description="Filter by topic",
    ),

    start_date: Optional[datetime] = Query(
        default=None,
        description="Return mentions published on or after this date",
    ),

    end_date: Optional[datetime] = Query(
        default=None,
        description="Return mentions published on or before this date",
    ),

    search_text: Optional[str] = Query(
        default=None,
        description="Search mention title or content",
    ),

    db: Session = Depends(get_db),
):
    """
    Get searchable and filterable mentions for a search.

    Supports:

    - Pagination
    - Source filtering
    - Sentiment filtering
    - Topic filtering
    - Date filtering
    - Text search
    """

    service = MentionService()

    result = service.get_mentions(
        db=db,
        search_id=search_id,
        page=page,
        page_size=page_size,
        source=source,
        sentiment=sentiment,
        topic=topic,
        start_date=start_date,
        end_date=end_date,
        search_text=search_text,
    )

    if result is None:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=404,
            detail="Search not found.",
        )

    return result