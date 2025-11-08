from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, String, ForeignKey, Index, VARCHAR
from sqlalchemy.orm import relationship, Mapped, mapped_column
from tprep.infrastructure.models import Base

if TYPE_CHECKING:
    from tprep.infrastructure.statistic.statistic import Statistic
    from tprep.infrastructure.user.user import User


class Exam(Base):
    __tablename__ = "exams"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    creator_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),  # passive_deletes УБРАТЬ
    )

    # many-to-one — каскад на пользователя обычно не нужен
    creator: Mapped["User"] = relationship("User", back_populates="created_exams")

    # one-to-many: ORM-удаления сирот и пассивные удаление через БД
    cards: Mapped[list["Card"]] = relationship(
        "Card",
        back_populates="exam",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    pinned_by: Mapped[list["UserPinnedExam"]] = relationship(
        "UserPinnedExam",
        back_populates="exam",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    related_stat: Mapped[list["Statistic"]] = relationship(
        "Statistic",
        back_populates="related_exam",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class UserPinnedExam(Base):
    __tablename__ = "user_pinned_exams"

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),  # passive_deletes УБРАТЬ
        primary_key=True,
        index=True,
    )
    exam_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("exams.id", ondelete="CASCADE"),  # passive_deletes УБРАТЬ
        primary_key=True,
        index=True,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="pinned_exams",
        passive_deletes=True,
    )
    exam: Mapped["Exam"] = relationship(
        "Exam",
        back_populates="pinned_by",
        passive_deletes=True,
    )

    __table_args__ = (Index("idx_user_pinned_user_id", "user_id"),)


class Card(Base):
    __tablename__ = "cards"

    card_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    exam_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("exams.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question: Mapped[str] = mapped_column(VARCHAR(500), nullable=False)
    answer: Mapped[str] = mapped_column(VARCHAR(500), nullable=False)
    number: Mapped[int] = mapped_column(BigInteger, nullable=False)

    exam: Mapped["Exam"] = relationship("Exam", back_populates="cards")

    __table_args__ = (Index("idx_cards_exam_id", "exam_id"),)

    related_stat: Mapped[list["Statistic"]] = relationship(
        "Statistic",
        back_populates="related_card",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
