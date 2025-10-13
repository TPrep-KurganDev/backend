from sqlalchemy import Column, BigInteger, String, ForeignKey, Index, VARCHAR
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)
    login = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    surname = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)

    pinned_exams = relationship("UserPinnedExam", back_populates="user")
    created_exams = relationship("UserCreatedExam", back_populates="user")


class Exam(Base):
    __tablename__ = "exams"

    id = Column(BigInteger, primary_key=True, index=True)
    title = Column(String(255), nullable=False)

    cards = relationship("Card", back_populates="exam")
    pinned_by = relationship("UserPinnedExam", back_populates="exam")
    created_by = relationship("UserCreatedExam", back_populates="exam")


class UserPinnedExam(Base):
    __tablename__ = "user_pinned_exams"

    user_id = Column(BigInteger, ForeignKey("users.id"), primary_key=True, index=True)
    exam_id = Column(BigInteger, ForeignKey("exams.id"), primary_key=True, index=True)

    user = relationship("User", back_populates="pinned_exams")
    exam = relationship("Exam", back_populates="pinned_by")

    __table_args__ = (
        Index("idx_user_pinned_user_id", "user_id"),
    )


class UserCreatedExam(Base):
    __tablename__ = "user_created_exams"

    user_id = Column(BigInteger, ForeignKey("users.id"), primary_key=True, index=True)
    exam_id = Column(BigInteger, ForeignKey("exams.id"), primary_key=True, index=True)

    user = relationship("User", back_populates="created_exams")
    exam = relationship("Exam", back_populates="created_by")

    __table_args__ = (
        Index("idx_user_created_user_id", "user_id"),
    )


class Card(Base):
    __tablename__ = "cards"

    number = Column(BigInteger, primary_key=True, index=True)
    exam_id = Column(BigInteger, ForeignKey("exams.id"), nullable=False, index=True)
    question = Column(VARCHAR(500), nullable=False)
    answer = Column(VARCHAR(500), nullable=False)

    exam = relationship("Exam", back_populates="cards")

    __table_args__ = (
        Index("idx_cards_exam_id", "exam_id"),
    )
