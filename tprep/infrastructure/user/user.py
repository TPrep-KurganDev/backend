from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from pydantic import EmailStr
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tprep.infrastructure.models import Base

if TYPE_CHECKING:
    from tprep.infrastructure import Exam, UserExams, Statistic, NotificationDB


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        index=True,
        default=uuid4,
    )
    email: Mapped["EmailStr"] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    user_name: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    push_key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    endpoint: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    auth_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    pinned_exams: Mapped[list["UserExams"]] = relationship(
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
