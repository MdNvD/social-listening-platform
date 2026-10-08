from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# =========================================================
# CREATE MONITORING
# =========================================================

class MonitoringCreate(BaseModel):
    keyword: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Brand, company, product, or keyword to monitor.",
    )

    interval_minutes: int = Field(
        default=1440,
        ge=5,
        le=10080,
        description="How often to collect new mentions, in minutes.",
    )

    is_active: bool = Field(
        default=True,
        description="Whether the monitoring schedule should be active.",
    )


# =========================================================
# UPDATE MONITORING
# =========================================================

class MonitoringUpdate(BaseModel):
    keyword: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=255,
        description="Updated keyword.",
    )

    interval_minutes: Optional[int] = Field(
        default=None,
        ge=5,
        le=10080,
        description="Updated interval in minutes.",
    )

    is_active: Optional[bool] = Field(
        default=None,
        description="Enable or disable the monitoring schedule.",
    )


# =========================================================
# MONITORING RESPONSE
# =========================================================

class MonitoringResponse(BaseModel):
    id: int
    keyword: str
    interval_minutes: int
    is_active: bool
    last_run_at: Optional[datetime]
    next_run_at: Optional[datetime]
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )