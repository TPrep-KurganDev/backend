from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from tprep.app.notification_schemas import NotificationOut
from tprep.infrastructure.authorization import get_current_user_id
from tprep.infrastructure.database import get_db
from tprep.infrastructure.exam.exam_repo import ExamRepo
from tprep.infrastructure.notification.notification_repo import NotificationRepo

router = APIRouter(tags=["Notifications"])


@router.get("/notifications", response_model=List[NotificationOut])
def get_notifications(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)) -> List[
    NotificationOut]:
    notifications = NotificationRepo.get_all_notifications_of_user(user_id=user_id, db=db)
    result = []
    for notification in notifications:
        result.append(
            NotificationOut(id=notification.id, exam_title=ExamRepo.get_exam(exam_id=notification.exam_id, db=db).title,
                            time=notification.time))
    return result

@router.delete("/notifications/{notification_id}", status_code=204)
def delete_notification(notification_id: int, db: Session = Depends(get_db)):
    NotificationRepo.delete_notification_by_id(notification_id=notification_id, db=db)