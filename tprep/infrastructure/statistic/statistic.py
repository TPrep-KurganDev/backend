from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import BigInteger, ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tprep.infrastructure import Base

if TYPE_CHECKING:
    from tprep.infrastructure import Card, Exam, User


class Statistic(Base):
    __tablename__ = "statistics"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    card_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("cards.card_id", ondelete="CASCADE"), index=True
    )
    exam_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("exams.id", ondelete="CASCADE"),
        index=True,
    )

    mistakes_count: Mapped[int] = mapped_column(BigInteger)

    related_card: Mapped["Card"] = relationship(
        "Card", back_populates="related_stat", passive_deletes=True
    )
    related_exam: Mapped["Exam"] = relationship(
        "Exam", back_populates="related_stat", passive_deletes=True
    )
    related_user: Mapped["User"] = relationship(
        "User", back_populates="related_stat", passive_deletes=True
    )

    __table_args__ = (
        Index("idx_statistics_user_id", "user_id"),
        Index("idx_statistics_card_id", "card_id"),
        Index("idx_statistics_exam_id", "exam_id"),
        UniqueConstraint(
            "user_id", "card_id", "exam_id", name="uq_statistics_user_card_exam"
        ),
    )
