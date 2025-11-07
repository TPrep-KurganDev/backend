from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, model_validator

from tprep.infrastructure.exceptions.wrong_n_value import WrongNValue


class ExamSessionResponse(BaseModel):
    id: int
    created_at: datetime
    user_id: int
    exam_id: int
    questions: List[int]
    answers: Optional[List[bool]] = None
    n: Optional[int] = None

    class Config:
        from_attributes = True


class ExamSessionStartRequest(BaseModel):
    user_id: int
    exam_id: int
    strategy: str = "random"
    n: Optional[int] = None

    @model_validator(mode="after")
    def check_n_allowed(self) -> "ExamSessionStartRequest":
        if self.n is not None:
            if self.strategy in ("smart", "full"):
                raise WrongNValue(
                    f"Parameter 'n' is not allowed for strategy '{self.strategy}'"
                )
            if self.n <= 0:
                raise WrongNValue("Parameter 'n' must be positive")
        return self

    class Config:
        from_attributes = True
