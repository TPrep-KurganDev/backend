from uuid import UUID
from pydantic import BaseModel


class ExamBase(BaseModel):
    title: str
    scope: str = "default"


class ExamCreate(ExamBase):
    pass


class ExamPinStatus(BaseModel):
    is_pinned: bool


class ExamRightsResponse(BaseModel):
    user_id: list[UUID]


class ExamOut(ExamBase):
    id: UUID
    creator_id: UUID

    class Config:
        from_attributes = True
