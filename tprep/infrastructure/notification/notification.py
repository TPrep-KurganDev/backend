from datetime import datetime
from sqlalchemy import BigInteger, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column
from infrastructure.models import Base

class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete='CASCADE'))
    exam_id: Mapped[int] = mapped_column(ForeignKey("exams.id", ondelete='CASCADE'))
    time: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    user: Mapped["User"] = relationship(
        "User", back_populates="user_notifications"
    )
    exam: Mapped["Exam"] = relationship(
        "Exam", back_populates="exam_notifications"
    )

    __table_args__ = (
        Index("idx_notifications_time", "time"),
    )
