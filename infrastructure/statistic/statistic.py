from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from infrastructure.models import Base


class Statistic(Base):
    __tablename__ = "statistics"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete='CASCADE'), primary_key=True, index=True)
    card_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("cards.card_id", ondelete='CASCADE'), primary_key=True, index=True)
    exam_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("exams.id", ondelete='CASCADE'), primary_key=True, index=True)
    mistakes_count: Mapped[int] = mapped_column(BigInteger)

    related_card: Mapped["Card"] = relationship(
        "Card", back_populates="related_stat"
    )

    related_exam: Mapped["Exam"] = relationship(
        "Exam", back_populates="related_stat"
    )

    related_user: Mapped["User"] = relationship(
        "User", back_populates="related_stat"
    )