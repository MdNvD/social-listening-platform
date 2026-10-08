from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Monitoring
from app.schemas.monitoring import (
    MonitoringCreate,
    MonitoringResponse,
    MonitoringUpdate,
)
from app.services.scheduler_service import scheduler_service


router = APIRouter(
    prefix="/api/monitorings",
    tags=["Scheduled Monitoring"],
)


# =========================================================
# CREATE MONITORING
# =========================================================

@router.post(
    "",
    response_model=MonitoringResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_monitoring(
    monitoring_data: MonitoringCreate,
    db: Session = Depends(get_db),
):
    keyword = monitoring_data.keyword.strip()

    if not keyword:
        raise HTTPException(
            status_code=400,
            detail="Keyword cannot be empty.",
        )

    monitoring = Monitoring(
        keyword=keyword,
        interval_minutes=monitoring_data.interval_minutes,
        is_active=monitoring_data.is_active,
    )

    db.add(monitoring)
    db.commit()
    db.refresh(monitoring)

    # Register the new monitoring with APScheduler.
    if monitoring.is_active:
        scheduler_service.add_monitoring(
            monitoring.id
        )

    return monitoring


# =========================================================
# LIST MONITORINGS
# =========================================================

@router.get(
    "",
    response_model=list[MonitoringResponse],
)
def get_monitorings(
    db: Session = Depends(get_db),
):
    monitorings = (
        db.query(Monitoring)
        .order_by(Monitoring.created_at.desc())
        .all()
    )

    return monitorings


# =========================================================
# GET ONE MONITORING
# =========================================================

@router.get(
    "/{monitoring_id}",
    response_model=MonitoringResponse,
)
def get_monitoring(
    monitoring_id: int,
    db: Session = Depends(get_db),
):
    monitoring = (
        db.query(Monitoring)
        .filter(Monitoring.id == monitoring_id)
        .first()
    )

    if monitoring is None:
        raise HTTPException(
            status_code=404,
            detail="Monitoring not found.",
        )

    return monitoring


# =========================================================
# UPDATE MONITORING
# =========================================================

@router.patch(
    "/{monitoring_id}",
    response_model=MonitoringResponse,
)
def update_monitoring(
    monitoring_id: int,
    monitoring_data: MonitoringUpdate,
    db: Session = Depends(get_db),
):
    monitoring = (
        db.query(Monitoring)
        .filter(Monitoring.id == monitoring_id)
        .first()
    )

    if monitoring is None:
        raise HTTPException(
            status_code=404,
            detail="Monitoring not found.",
        )

    update_data = monitoring_data.model_dump(
        exclude_unset=True
    )

    if "keyword" in update_data:
        keyword = update_data["keyword"].strip()

        if not keyword:
            raise HTTPException(
                status_code=400,
                detail="Keyword cannot be empty.",
            )

        monitoring.keyword = keyword

    if "interval_minutes" in update_data:
        monitoring.interval_minutes = (
            update_data["interval_minutes"]
        )

    if "is_active" in update_data:
        monitoring.is_active = (
            update_data["is_active"]
        )

    db.commit()
    db.refresh(monitoring)

    # Re-register or remove the APScheduler job
    # according to the new state.
    if monitoring.is_active:
        scheduler_service.add_monitoring(
            monitoring.id
        )
    else:
        scheduler_service.remove_monitoring(
            monitoring.id
        )

    return monitoring


# =========================================================
# DELETE MONITORING
# =========================================================

@router.delete(
    "/{monitoring_id}",
)
def delete_monitoring(
    monitoring_id: int,
    db: Session = Depends(get_db),
):
    monitoring = (
        db.query(Monitoring)
        .filter(Monitoring.id == monitoring_id)
        .first()
    )

    if monitoring is None:
        raise HTTPException(
            status_code=404,
            detail="Monitoring not found.",
        )

    # Remove the APScheduler job first.
    scheduler_service.remove_monitoring(
        monitoring.id
    )

    db.delete(monitoring)
    db.commit()

    return {
        "message": "Monitoring deleted successfully.",
        "id": monitoring_id,
    }