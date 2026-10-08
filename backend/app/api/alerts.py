import traceback

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Search
from app.services.alert_service import AlertService


router = APIRouter(
    prefix="/api/searches",
    tags=["Alerts"],
)


@router.get("/{search_id}/alerts")
def get_alerts(
    search_id: int,
    db: Session = Depends(get_db),
):

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

    if search.status != "completed":

        raise HTTPException(
            status_code=400,
            detail=(
                "Alerts can only be calculated "
                "for completed searches."
            ),
        )

    service = AlertService()

    try:

        result = service.get_alerts(
            db=db,
            search_id=search_id,
        )

        return {
            "search_id": search.id,
            "keyword": search.keyword,
            "status": search.status,
            **result,
        }

    except Exception as error:

        print(
            "\n"
            + "=" * 70
        )

        print(
            "ALERT PROCESSING ERROR"
        )

        print(
            "=" * 70
        )

        print(
            f"Error type: "
            f"{type(error).__name__}"
        )

        print(
            f"Error message: {error}"
        )

        print(
            "\nFULL TRACEBACK:"
        )

        traceback.print_exc()

        print(
            "=" * 70
            + "\n"
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to calculate alerts.",
        ) from error