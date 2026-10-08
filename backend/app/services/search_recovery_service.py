from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.database.models import Search


STALE_SEARCH_MINUTES = 30


def recover_stale_searches() -> int:
    """
    Mark searches that have been stuck in 'running' state
    for longer than STALE_SEARCH_MINUTES as failed.

    This handles cases where the application was stopped or
    crashed before the normal exception handler could update
    the search status.
    """

    db: Session = SessionLocal()

    try:
        cutoff = datetime.now(timezone.utc) - timedelta(
            minutes=STALE_SEARCH_MINUTES
        )

        stale_searches = (
            db.query(Search)
            .filter(
                Search.status == "running",
                Search.started_at.isnot(None),
                Search.started_at < cutoff,
            )
            .all()
        )

        if not stale_searches:
            print("No stale running searches found.")
            return 0

        recovered_count = 0

        for search in stale_searches:
            search.status = "failed"

            print(
                f"Recovered stale search #{search.id}: "
                f"'{search.keyword}'"
            )

            recovered_count += 1

        db.commit()

        print(
            f"Recovered {recovered_count} stale search(es)."
        )

        return recovered_count

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()
