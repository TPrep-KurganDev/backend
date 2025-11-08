from pydantic import BaseModel

class CardBase(BaseModel):
    question: str
    answer: str