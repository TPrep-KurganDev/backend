from dataclasses import dataclass

from openai import OpenAI

from config import settings
from tprep.infrastructure.exceptions.ai_generation_failed import AiGenerationFailed


@dataclass
class GenerationResult:
    card_id: int
    answer: str | None
    success: bool
    error: str | None = None


class AiAnswerGenerator:
    MODEL = "arcee-ai/trinity-large-preview:free"
    MAX_ANSWER_LENGTH = 490

    SYSTEM_PROMPT = (
        "You are an educational assistant. Given a question from a study card, "
        "provide a concise, accurate answer. The answer MUST be no longer than "
        "300 characters. Be direct and factual. Do not include prefixes like "
        "'Answer:' — just provide the answer content."
        "Answer in russian"
    )

    def __init__(self) -> None:
        if not settings.OPENROUTER_API_KEY:
            raise AiGenerationFailed("OPENROUTER_API_KEY is not configured")
        self._client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.OPENROUTER_API_KEY,
        )

    def generate_answer(self, question: str) -> str:
        try:
            response = self._client.chat.completions.create(
                model=self.MODEL,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": question},
                ],
                max_tokens=256,
                temperature=0.3,
            )
            text = response.choices[0].message.content
            if text is None:
                raise AiGenerationFailed(
                    f"Empty response for question: {question[:50]}"
                )
            return text[: self.MAX_ANSWER_LENGTH]
        except AiGenerationFailed:
            raise
        except Exception as e:
            raise AiGenerationFailed(
                f"OpenRouter API error for question '{question[:50]}...': {e}"
            )

    def generate_answers_batch(
        self, cards: list[tuple[int, str]]
    ) -> list[GenerationResult]:
        results: list[GenerationResult] = []
        for card_id, question in cards:
            if not question.strip():
                results.append(
                    GenerationResult(
                        card_id=card_id,
                        answer=None,
                        success=False,
                        error="Empty question, cannot generate answer",
                    )
                )
                continue
            try:
                answer = self.generate_answer(question)
                results.append(
                    GenerationResult(card_id=card_id, answer=answer, success=True)
                )
            except AiGenerationFailed as e:
                results.append(
                    GenerationResult(
                        card_id=card_id, answer=None, success=False, error=e.message
                    )
                )
        return results