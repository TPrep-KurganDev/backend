from pydantic import BaseModel


class CardBase(BaseModel):
    question: str
    answer: str


class CardResponse(CardBase):
    card_id: int
    number: int

    class Config:
        from_attributes = True


class GenerateAnswersRequest(BaseModel):
    card_ids: list[int] | None = None


class CardGenerationResult(BaseModel):
    card_id: int
    number: int
    question: str
    answer: str
    success: bool
    error: str | None = None

    class Config:
        from_attributes = True


class GenerateAnswersResponse(BaseModel):
    total: int
    successful: int
    failed: int
    cards: list[CardGenerationResult]
