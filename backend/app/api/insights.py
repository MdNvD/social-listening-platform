from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Search
from app.services.ai_insights_service import (
    AIInsightsService,
)


router = APIRouter(
    prefix="/api/searches",
    tags=["AI Insights"],
)


@router.get(
    "/{search_id}/insights"
)
def get_ai_insights(
    search_id: int,
    db: Session = Depends(get_db),
):
    """
    Build deterministic evidence and generate
    AI-powered insights for a completed search.
    """

    # ---------------------------------------------------------
    # Verify search exists
    # ---------------------------------------------------------

    search = (
        db.query(Search)
        .filter(
            Search.id == search_id
        )
        .first()
    )

    if search is None:
        raise HTTPException(
            status_code=404,
            detail="Search not found.",
        )

    # ---------------------------------------------------------
    # Verify search status
    # ---------------------------------------------------------

    if search.status != "completed":
        raise HTTPException(
            status_code=400,
            detail=(
                "AI insights can only be generated "
                "for completed searches."
            ),
        )

    # ---------------------------------------------------------
    # Build evidence + generate AI insights
    # ---------------------------------------------------------

    service = AIInsightsService()

    try:
        result = service.build_complete_insights(
            db=db,
            search_id=search_id,
            keyword=search.keyword,
        )

    except RuntimeError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to generate AI insights."
            ),
        ) from error

    # ---------------------------------------------------------
    # Return complete response
    # ---------------------------------------------------------

    return {
        "search_id": search.id,
        "keyword": search.keyword,
        "status": search.status,
        "evidence": result["evidence"],
        "ai_insights": result["ai_insights"],
    }