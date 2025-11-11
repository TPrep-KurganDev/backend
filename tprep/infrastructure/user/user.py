from typing import TYPE_CHECKING, Optional

from pydantic import EmailStr
from sqlalchemy import BigInteger, String
from sqlalchemy.orm import relationship, Mapped, mapped_column
from tprep.infrastructure.models import Base
from tprep.infrastructure.notification.notificationdb import NotificationDB

if TYPE_CHECKING:
    from tprep.infrastructure.exam.exam import Exam, UserPinnedExam
    from tprep.infrastructure.statistic.statistic import Statistic


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    email: Mapped["EmailStr"] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    user_name: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    push_key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    endpoint: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    auth_token: Mapped[str] = mapped_column(String(255), nullable=True)

    pinned_exams: Mapped[list["UserPinnedExam"]] = relationship(
        "UserPinnedExam",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    created_exams: Mapped[list["Exam"]] = relationship(
        "Exam",
        back_populates="creator",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    related_stat: Mapped[list["Statistic"]] = relationship(
        "Statistic",
        back_populates="related_user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    related_notification: Mapped[list["NotificationDB"]] = relationship(
        "NotificationDB",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
