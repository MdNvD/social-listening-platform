import traceback

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services.competitor_service import (
    CompetitorService,
)


router = APIRouter(
    prefix="/api/competitors",
    tags=["Competitors"],
)


# =========================================================
# Request schema
# =========================================================

class CompetitorComparisonRequest(
    BaseModel
):

    keywords: list[str] = Field(
        ...,
        min_length=2,
        max_length=5,
        description=(
            "Two to five brands, products, "
            "or keywords to compare."
        ),
    )

    limit_per_source: int = Field(
        default=10,
        ge=1,
        le=50,
    )


# =========================================================
# Comparison endpoint
# =========================================================

@router.post("/compare")
def compare_competitors(
    request: CompetitorComparisonRequest,
    db: Session = Depends(get_db),
):

    service = CompetitorService()

    try:

        result = service.compare(
            db=db,
            keywords=request.keywords,
            limit_per_source=(
                request.limit_per_source
            ),
        )

        return result

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:

        print(
            "\n"
            + "=" * 70
        )

        print(
            "COMPETITOR COMPARISON ERROR"
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
            detail=(
                "Competitor comparison failed."
            ),
        ) from error