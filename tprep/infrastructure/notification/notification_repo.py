from datetime import datetime, timezone, timedelta

from fastapi import Depends
from sqlalchemy.orm import Session

from tprep.infrastructure.database import get_db
from tprep.infrastructure.notification.notification import Notification


class NotificationRepo:
    INTERVALS = [
        timedelta(minutes=20),
        timedelta(hours=8),
        timedelta(days=1)
    ]

    @staticmethod
    def create_notification(user_id: int, exam_id: int, db: Session = Depends(get_db)):
        now = datetime.now(timezone.utc)
        for delta in NotificationRepo.INTERVALS:
            notification = Notification(
                user_id=user_id,
                exam_id=exam_id,
                time=now + delta
            )
            db.add(notification)

        db.commit()

    @staticmethod
    def delete_notification(user_id: int, exam_id: int, db: Session = Depends(get_db)):
        notification = db.query(Notification).filter(Notification.user_id == user_id, Notification.exam_id == exam_id).first()
        if notification:
            db.delete(notification)
            db.commit()
