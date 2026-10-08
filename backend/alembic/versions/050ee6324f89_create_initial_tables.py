"""create initial tables

Revision ID: 050ee6324f89
Revises:
Create Date: 2026-09-29 13:24:02.344196

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "050ee6324f89"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "searches",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("keyword", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("total_collected", sa.Integer(), nullable=False),
        sa.Column("total_processed", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_searches_keyword"),
        "searches",
        ["keyword"],
        unique=False,
    )

    op.create_table(
        "mentions",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("search_id", sa.BigInteger(), nullable=False),
        sa.Column("source", sa.String(length=50), nullable=False),
        sa.Column("source_id", sa.String(length=255), nullable=True),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("author", sa.String(length=255), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("keyword", sa.String(length=255), nullable=False),
        sa.Column("engagement", sa.Integer(), nullable=False),
        sa.Column(
            "collected_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["search_id"],
            ["searches.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_mentions_search_id"),
        "mentions",
        ["search_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_mentions_source"),
        "mentions",
        ["source"],
        unique=False,
    )

    op.create_index(
        op.f("ix_mentions_keyword"),
        "mentions",
        ["keyword"],
        unique=False,
    )

    op.create_table(
        "mention_analysis",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("mention_id", sa.BigInteger(), nullable=False),
        sa.Column("relevance_score", sa.Float(), nullable=True),
        sa.Column("is_relevant", sa.Boolean(), nullable=False),
        sa.Column("is_duplicate", sa.Boolean(), nullable=False),
        sa.Column("duplicate_of", sa.BigInteger(), nullable=True),
        sa.Column("sentiment", sa.String(length=20), nullable=True),
        sa.Column("sentiment_confidence", sa.Float(), nullable=True),
        sa.Column("topic", sa.String(length=50), nullable=True),
        sa.Column("topic_confidence", sa.Float(), nullable=True),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["mention_id"],
            ["mentions.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("mention_id"),
    )

    op.create_index(
        op.f("ix_mention_analysis_mention_id"),
        "mention_analysis",
        ["mention_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_table("mention_analysis")

    op.drop_index(
        op.f("ix_mentions_keyword"),
        table_name="mentions",
    )

    op.drop_index(
        op.f("ix_mentions_source"),
        table_name="mentions",
    )

    op.drop_index(
        op.f("ix_mentions_search_id"),
        table_name="mentions",
    )

    op.drop_table("mentions")

    op.drop_index(
        op.f("ix_searches_keyword"),
        table_name="searches",
    )

    op.drop_table("searches")