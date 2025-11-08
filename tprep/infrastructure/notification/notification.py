from typing import TYPE_CHECKING

from datetime import datetime
from sqlalchemy import BigInteger, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column
from tprep.infrastructure.models import Base

if TYPE_CHECKING:
    from tprep.infrastructure.exam.exam import Exam
    from tprep.infrastructure.user.user import User


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete='CASCADE'))
    exam_id: Mapped[int] = mapped_column(ForeignKey("exams.id", ondelete='CASCADE'))
    time: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    user: Mapped["User"] = relationship(
        "User", back_populates="related_notifications"
    )
    exam: Mapped["Exam"] = relationship(
        "Exam", back_populates="related_notifications"
    )

    __table_args__ = (
        Index("idx_notifications_time", "time"),
    )

