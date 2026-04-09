"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-04-09 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop all existing tables and indexes to reset schema (data is not preserved)
    op.execute("DROP INDEX IF EXISTS idx_notifications_time")
    op.execute("DROP INDEX IF EXISTS idx_statistics_exam_id")
    op.execute("DROP INDEX IF EXISTS idx_statistics_card_id")
    op.execute("DROP INDEX IF EXISTS idx_statistics_user_id")
    op.execute("DROP INDEX IF EXISTS idx_cards_exam_id")
    op.execute("DROP INDEX IF EXISTS idx_user_pinned_user_id")
    op.execute("DROP TABLE IF EXISTS notifications CASCADE")
    op.execute("DROP TABLE IF EXISTS statistics CASCADE")
    op.execute("DROP TABLE IF EXISTS user_exams CASCADE")
    op.execute("DROP TABLE IF EXISTS cards CASCADE")
    op.execute("DROP TABLE IF EXISTS exams CASCADE")
    op.execute("DROP TABLE IF EXISTS users CASCADE")

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, index=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True, index=True),
        sa.Column("user_name", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("push_key", sa.String(255), nullable=True),
        sa.Column("endpoint", sa.String(512), nullable=True),
        sa.Column("auth_token", sa.String(255), nullable=True),
    )

    op.create_table(
        "exams",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, index=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("scope", sa.String(255), nullable=False, server_default="default"),
        sa.Column(
            "creator_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
    )

    op.create_table(
        "user_exams",
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "exam_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("exams.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("rights", sa.String(255), nullable=False),
        sa.Column("is_pinned", sa.Boolean, nullable=False, server_default="false"),
    )
    op.create_index("idx_user_pinned_user_id", "user_exams", ["user_id"])

    op.create_table(
        "cards",
        sa.Column("card_id", sa.BigInteger, primary_key=True),
        sa.Column(
            "exam_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("exams.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("question", sa.VARCHAR(500), nullable=False),
        sa.Column("answer", sa.VARCHAR(500), nullable=False),
        sa.Column("number", sa.BigInteger, nullable=False),
    )
    op.create_index("idx_cards_exam_id", "cards", ["exam_id"])

    op.create_table(
        "statistics",
        sa.Column("id", sa.BigInteger, primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "card_id",
            sa.BigInteger,
            sa.ForeignKey("cards.card_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "exam_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("exams.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("mistakes_count", sa.BigInteger, nullable=False),
        sa.UniqueConstraint("user_id", "card_id", "exam_id", name="uq_statistics_user_card_exam"),
    )
    op.create_index("idx_statistics_user_id", "statistics", ["user_id"])
    op.create_index("idx_statistics_card_id", "statistics", ["card_id"])
    op.create_index("idx_statistics_exam_id", "statistics", ["exam_id"])

    op.create_table(
        "notifications",
        sa.Column("id", sa.BigInteger, primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "exam_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("exams.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("time", sa.DateTime, nullable=False),
    )
    op.create_index("idx_notifications_time", "notifications", ["time"])


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS notifications CASCADE")
    op.execute("DROP TABLE IF EXISTS statistics CASCADE")
    op.execute("DROP TABLE IF EXISTS user_exams CASCADE")
    op.execute("DROP TABLE IF EXISTS cards CASCADE")
    op.execute("DROP TABLE IF EXISTS exams CASCADE")
    op.execute("DROP TABLE IF EXISTS users CASCADE")