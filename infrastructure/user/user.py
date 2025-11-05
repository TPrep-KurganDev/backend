from pydantic import EmailStr
from sqlalchemy import BigInteger, String
from sqlalchemy.orm import relationship, Mapped, mapped_column
from infrastructure.models import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    email: Mapped["EmailStr"] = mapped_column(String(255), unique=True, nullable=False, index=True)
    user_name: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    auth_token: Mapped[str] = mapped_column(String(255), nullable=True)
    push_key: Mapped[str] = mapped_column(String(255), nullable=True)

    pinned_exams: Mapped[list["UserPinnedExam"]] = relationship(
        "UserPinnedExam", back_populates="user", cascade="all, delete-orphan"
    )
    created_exams: Mapped[list["Exam"]] = relationship(
        "Exam", back_populates="creator", cascade="all, delete-orphan"
    )
    related_stat: Mapped[list["Statistic"]] = relationship(
        "Statistic",back_populates="related_user", cascade="all, delete-orphan"
    )

    user_notifications: Mapped[list["Notification"]] = relationship(
        "Notification", back_populates="user", cascade="all, delete-orphan"
    )