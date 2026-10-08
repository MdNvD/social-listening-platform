from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base


# =========================================================
# Search
# =========================================================

class Search(Base):
    __tablename__ = "searches"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    keyword: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="pending",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    total_collected: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    total_processed: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    mentions: Mapped[list["Mention"]] = relationship(
        back_populates="search",
        cascade="all, delete-orphan",
    )


# =========================================================
# Mention
# =========================================================

class Mention(Base):
    __tablename__ = "mentions"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    search_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "searches.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    # Changed from String(255) to Text.
    #
    # Some sources, especially Google News RSS, can provide
    # very long source identifiers.
    source_id: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    title: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    author: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    published_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    keyword: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    engagement: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    collected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    search: Mapped["Search"] = relationship(
        back_populates="mentions",
    )

    analysis: Mapped[Optional["MentionAnalysis"]] = relationship(
        back_populates="mention",
        uselist=False,
        cascade="all, delete-orphan",
    )


# =========================================================
# Mention Analysis
# =========================================================

class MentionAnalysis(Base):
    __tablename__ = "mention_analysis"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    mention_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "mentions.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
        index=True,
    )

    relevance_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    is_relevant: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    is_duplicate: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    duplicate_of: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        nullable=True,
    )

    sentiment: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )

    sentiment_confidence: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    topic: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    topic_confidence: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    processed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    mention: Mapped["Mention"] = relationship(
        back_populates="analysis",
    )


# =========================================================
# Scheduled Monitoring
# =========================================================

class Monitoring(Base):
    __tablename__ = "monitorings"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    keyword: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    interval_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1440,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    last_run_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    next_run_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )