from typing import TYPE_CHECKING
from uuid import UUID

from datetime import datetime
from sqlalchemy import BigInteger, ForeignKey, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tprep.infrastructure.models import Base

if TYPE_CHECKING:
    from tprep.infrastructure import Exam, User


class NotificationDB(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE")
    )
    exam_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("exams.id", ondelete="CASCADE")
    )
    time: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="related_notification")
    exam: Mapped["Exam"] = relationship("Exam", back_populates="related_notification")

    __table_args__ = (Index("idx_notifications_time", "time"),)
