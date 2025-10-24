from pydantic import EmailStr
from sqlalchemy import BigInteger, String
from sqlalchemy.orm import relationship, Mapped, mapped_column
from infrastructure.models import Base
from infrastructure.exam.exam import UserCreatedExam, UserPinnedExam

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    email: Mapped["EmailStr"] = mapped_column(String(255), unique=True, nullable=False, index=True)
    user_name: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    pinned_exams: Mapped[list["UserPinnedExam"]] = relationship(
        "UserPinnedExam", back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )
    created_exams: Mapped[list["UserCreatedExam"]] = relationship(
        "UserCreatedExam", back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )