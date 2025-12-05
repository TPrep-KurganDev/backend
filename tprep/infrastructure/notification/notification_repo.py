from datetime import datetime, timezone, timedelta
from typing import List

from fastapi import Depends
from sqlalchemy.orm import Session

from tprep.infrastructure.database import get_db
from tprep.infrastructure import NotificationDB


class NotificationRepo:
    INTERVALS = [timedelta(minutes=1), timedelta(minutes=20), timedelta(hours=8), timedelta(days=1)]

    @staticmethod
    def create_notification(
        user_id: int, exam_id: int, db: Session = Depends(get_db)
    ) -> None:
        now = datetime.now(timezone.utc)
        for delta in NotificationRepo.INTERVALS:
            notification = NotificationDB(
                user_id=user_id, exam_id=exam_id, time=now + delta
            )
            db.add(notification)

        db.commit()

    @staticmethod
    def delete_notification(
        user_id: int, exam_id: int, db: Session = Depends(get_db)
    ) -> None:
        notification = (
            db.query(NotificationDB)
            .filter(
                NotificationDB.user_id == user_id, NotificationDB.exam_id == exam_id
            )
            .first()
        )
        if notification:
            db.delete(notification)
            db.commit()

    @staticmethod
    def delete_notification_by_id(
        notification_id: int, db: Session = Depends(get_db)
    ):
        db.query(NotificationDB).filter(NotificationDB.id == notification_id).delete()

    @staticmethod
    def get_all_notifications_of_user(user_id: int, db: Session = Depends(get_db)) -> List[NotificationDB]:
        return db.query(NotificationDB).filter(NotificationDB.user_id == user_id).all()
