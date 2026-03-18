from enum import StrEnum
from uuid import UUID
from pydantic import BaseModel


class ExamScope(StrEnum):
    default = "default"
    link = "link"
    personal = "personal"


class ExamBase(BaseModel):
    title: str
    scope: ExamScope = ExamScope.default


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
