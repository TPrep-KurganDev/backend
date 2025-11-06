from pydantic import BaseModel


class ExamBase(BaseModel):
    title: str


class ExamCreate(ExamBase):
    pass


class ExamOut(ExamBase):
    id: int

    class Config:
        from_attributes = True
