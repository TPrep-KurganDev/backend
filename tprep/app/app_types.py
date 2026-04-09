from typing import NewType
from uuid import UUID

UserId = NewType("UserId", UUID)
CardId = NewType("CardId", int)
ExamId = NewType("ExamId", UUID)
NotificationId = NewType("NotificationId", int)
