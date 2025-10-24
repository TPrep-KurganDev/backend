from sqlalchemy import BigInteger, String, ForeignKey, Index, VARCHAR
from sqlalchemy.orm import relationship, Mapped, mapped_column
from infrastructure.models import Base
from infrastructure.user.user import User


class Exam(Base):
    __tablename__ = "exams"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)

    cards: Mapped[list["Card"]] = relationship(
        "Card", back_populates="exam", cascade="all, delete-orphan",passive_deletes=True
    )
    pinned_by: Mapped[list["UserPinnedExam"]] = relationship(
        "UserPinnedExam", back_populates="exam", cascade="all, delete-orphan", passive_deletes=True
    )
    created_by: Mapped[list["UserCreatedExam"]] = relationship(
        "UserCreatedExam", back_populates="exam", cascade="all, delete-orphan", passive_deletes=True
    )


class UserPinnedExam(Base):
    __tablename__ = "user_pinned_exams"

    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete='CASCADE', passive_deletes=True), primary_key=True, index=True)
    exam_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("exams.id", ondelete='CASCADE', passive_deletes=True), primary_key=True, index=True)

    user: Mapped["user"] = relationship("User", back_populates="pinned_exams")
    exam: Mapped["Exam"] = relationship("Exam", back_populates="pinned_by")

    __table_args__ = (
        Index("idx_user_pinned_user_id", "user_id"),
    )


class UserCreatedExam(Base):
    __tablename__ = "user_created_exams"

    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete='CASCADE', passive_deletes=True), primary_key=True, index=True)
    exam_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("exams.id", ondelete='CASCADE', passive_deletes=True), primary_key=True, index=True)

    user: Mapped["user"] = relationship("User", back_populates="created_exams")
    exam: Mapped["Exam"] = relationship("Exam", back_populates="created_by")

    __table_args__ = (
        Index("idx_user_created_user_id", "user_id"),
    )


class Card(Base):
    __tablename__ = "cards"

    number: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    exam_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("exams.id", ondelete='CASCADE', passive_deletes=True), nullable=False, index=True)
    question: Mapped[str] = mapped_column(VARCHAR(500), nullable=False)
    answer: Mapped[str] = mapped_column(VARCHAR(500), nullable=False)

    exam: Mapped["Exam"] = relationship("Exam", back_populates="cards")

    __table_args__ = (
        Index("idx_cards_exam_id", "exam_id"),
    )
