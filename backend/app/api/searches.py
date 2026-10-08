import traceback

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Search
from app.schemas.search import SearchCreate, SearchResponse
from app.services.search_persistence_service import (
    SearchPersistenceService,
)
from app.services.search_service import SearchService


router = APIRouter(
    prefix="/api/searches",
    tags=["Searches"],
)


# ============================================================
# CREATE SEARCH
# ============================================================

@router.post(
    "",
    response_model=SearchResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_search(
    search_data: SearchCreate,
    db: Session = Depends(get_db),
):
    """
    Create and execute a keyword search.

    Flow:

        Create search
            ↓
        Collect mentions
            ↓
        Process mentions
            ↓
        Save relevant mentions
            ↓
        Mark search completed
    """

    keyword = search_data.keyword.strip()

    if not keyword:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Keyword cannot be empty.",
        )

    # ---------------------------------------------------------
    # Step 1: Create search record
    # ---------------------------------------------------------

    search = Search(
        keyword=keyword,
        status="pending",
    )

    db.add(search)
    db.commit()
    db.refresh(search)

    persistence_service = SearchPersistenceService()

    try:
        # -----------------------------------------------------
        # Step 2: Mark search as running
        # -----------------------------------------------------

        persistence_service.mark_search_started(
            db=db,
            search=search,
        )

        # -----------------------------------------------------
        # Step 3: Collect + process mentions
        # -----------------------------------------------------

        search_service = SearchService()

        result = search_service.run_search(
            keyword=keyword,
            limit_per_source=10,
        )

        # -----------------------------------------------------
        # Step 4: Save processed results
        # -----------------------------------------------------

        persistence_service.save_search_results(
            db=db,
            search=search,
            processed_mentions=result[
                "processed_mentions"
            ],
            raw_count=len(
                result["raw_mentions"]
            ),
        )

        # -----------------------------------------------------
        # Step 5: Mark search as completed
        # -----------------------------------------------------

        persistence_service.mark_search_completed(
            db=db,
            search=search,
        )

        db.refresh(search)

        return search

    except Exception as error:
        # -----------------------------------------------------
        # Print the real error to the terminal.
        # -----------------------------------------------------

        print("\n" + "=" * 70)
        print("SEARCH PROCESSING ERROR")
        print("=" * 70)

        print(
            f"Error type: {type(error).__name__}"
        )

        print(
            f"Error message: {error}"
        )

        print("\nFULL TRACEBACK:")

        traceback.print_exc()

        print("=" * 70 + "\n")

        # -----------------------------------------------------
        # Roll back the failed database transaction.
        # -----------------------------------------------------

        db.rollback()

        # -----------------------------------------------------
        # Try to mark the search as failed.
        # -----------------------------------------------------

        try:
            search = (
                db.query(Search)
                .filter(
                    Search.id == search.id
                )
                .first()
            )

            if search is not None:
                persistence_service.mark_search_failed(
                    db=db,
                    search=search,
                )

        except Exception as failure_error:

            print("\n" + "=" * 70)
            print(
                "FAILED TO MARK SEARCH AS FAILED"
            )
            print("=" * 70)

            print(
                f"Error: {failure_error}"
            )

            traceback.print_exc()

            print("=" * 70 + "\n")

        # -----------------------------------------------------
        # Return safe API error to the client.
        # -----------------------------------------------------

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search processing failed.",
        )


# ============================================================
# SEARCH HISTORY
# ============================================================

@router.get(
    "",
    response_model=list[SearchResponse],
)
def get_search_history(
    db: Session = Depends(get_db),
):
    """
    Get all previous searches.

    Results are ordered from newest to oldest.

    Scheduled monitoring runs are also included because
    the scheduler creates normal Search records.
    """

    searches = (
        db.query(Search)
        .order_by(
            Search.created_at.desc()
        )
        .all()
    )

    return searches


# ============================================================
# GET SINGLE SEARCH
# ============================================================

@router.get(
    "/{search_id}",
    response_model=SearchResponse,
)
def get_search(
    search_id: int,
    db: Session = Depends(get_db),
):
    """
    Get the status and statistics of a single search.
    """

    search = (
        db.query(Search)
        .filter(
            Search.id == search_id
        )
        .first()
    )

    if search is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Search not found.",
        )

    return search