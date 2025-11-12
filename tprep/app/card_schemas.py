from typing import List
from pydantic import BaseModel


class CardBase(BaseModel):
    question: str
    answer: str

class CardResponse(CardBase):
    card_id: int
    number: int

    class Config:
        from_attributes = True