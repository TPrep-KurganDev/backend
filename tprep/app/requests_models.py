from datetime import datetime

from pydantic import BaseModel

from tprep.app.app_types import NotificationId, UserId, ExamId
from tprep.infrastructure import NotificationDB


class Notification(BaseModel):
    id: NotificationId
    user_id: UserId
    exam_id: ExamId
    time: datetime

    @classmethod
    def from_db_model(cls, model: NotificationDB) -> "Notification":
        return Notification(
            id=NotificationId(model.id),
            user_id=UserId(model.user_id),
            exam_id=ExamId(model.exam_id),
            time=model.time,
        )


class StatusResponse(BaseModel):
    status: str
