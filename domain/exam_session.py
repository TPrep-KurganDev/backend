from dataclasses import field
from datetime import datetime
from typing import List
from uuid import uuid4

from infrastructure.exceptions.question_not_in_session import QuestionNotInSession
from infrastructure.statistic.stat_repo import StatRepo


class ExamSession:
    def __init__(self, user_id: int, exam_id: int, questions: List[int]):
        self.user_id: int = user_id
        self.exam_id: int = exam_id
        self.questions: List[int] = questions

        self.id: str = field(default_factory=lambda: str(uuid4()))
        self.created_at: datetime = field(default_factory=datetime.utcnow)

        self._answers: dict[int, bool] = field(default_factory=dict)

    def set_answer(self, question_id: int, is_right: bool) -> None:
        if question_id not in self.questions:
            raise QuestionNotInSession(f"Question {question_id} is not part of this session.")
        self._answers[question_id] = is_right
        if not is_right:
            StatRepo.inc_mistakes(self.user_id, question_id)


