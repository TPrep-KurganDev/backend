from pydantic import BaseModel


class ExamBase(BaseModel):
    title: str


class ExamCreate(ExamBase):
    pass


class ExamPinStatus(BaseModel):
    is_pinned: bool


class ExamOut(ExamBase):
    id: int
    creator_id: int

    class Config:
        from_attributes = True
