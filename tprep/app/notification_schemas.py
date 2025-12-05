import datetime

from pydantic import BaseModel

class NotificationOut(BaseModel):
    id: int
    exam_title: str
    time: datetime.datetime