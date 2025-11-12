from pydantic import BaseModel

class CardBase(BaseModel):
    question: str
    answer: str

class CardCreate(CardBase):
    card_id: int