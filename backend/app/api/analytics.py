from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.analytics import AnalyticsResponse
from app.services.analytics_service import AnalyticsService


router = APIRouter(
    prefix="/api/searches",
    tags=["Analytics"],
)


@router.get(
    "/{search_id}/analytics",
    response_model=AnalyticsResponse,
)
def get_search_analytics(
    search_id: int,
    db: Session = Depends(get_db),
):
    """
    Get analytics for a specific search.

    Returns:

    - Total collected mentions
    - Total processed mentions
    - Total unique relevant mentions
    - Sentiment distribution
    - Topic distribution
    - Source distribution
    - Mentions over time
    - First mention timestamp
    - Last mention timestamp
    """

    service = AnalyticsService()

    analytics = service.get_search_analytics(
        db=db,
        search_id=search_id,
    )

    if analytics is None:
        raise HTTPException(
            status_code=404,
            detail="Search not found.",
        )

    return analytics