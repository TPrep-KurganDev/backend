from uuid import UUID

from pydantic import BaseModel


class ExamBase(BaseModel):
    title: str


class ExamCreate(ExamBase):
    pass


class ExamPinStatus(BaseModel):
    is_pinned: bool


class ExamOut(ExamBase):
    id: UUID
    creator_id: UUID

    class Config:
        from_attributes = True
