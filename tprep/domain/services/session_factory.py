from random import sample

from fastapi import Depends
from sqlalchemy.orm import Session

from tprep.domain.exam_session import ExamSession
from tprep.infrastructure.exam.exam import Exam, Card
from tprep.infrastructure.exceptions.UnexceptableStrategy import UnexceptableStrategy
from tprep.infrastructure.exceptions.exam_has_no_cards import ExamHasNoCards
from tprep.infrastructure.statistic.statistic import Statistic
from tprep.infrastructure.user.user import User
from tprep.infrastructure.database import get_db


strategy_enum = ["full", "random", "smart"]


class SessionFactory:
    session_ids: dict[str, ExamSession] = {}

    @staticmethod
    def create_session(
        user: User,
        exam: Exam,
        strategy: str = "full",
        n: int = None,
        db: Session = Depends(get_db),
    ) -> ExamSession:
        cards = db.query(Card).filter(Card.exam_id == exam.id).all()

        if not cards:
            raise ExamHasNoCards("Exam has no cards.")

        if strategy == "random":
            selected_cards = sample(cards, min(n, len(cards)))
        elif strategy == "full":
            selected_cards = cards
        elif strategy == "smart":
            limit = SessionFactory.smart_session_size(len(cards))
            selected_cards = SessionFactory.get_smart_cards(user.id, exam.id, limit, db)
        else:
            raise UnexceptableStrategy(f"Unknow strategy: {strategy}")

        session = ExamSession(user.id, exam.id, selected_cards)

        SessionFactory.session_ids[session.id] = session

        return session

    @staticmethod
    def get_session_by_id(session_id: int) -> ExamSession:
        return SessionFactory.session_ids[str(session_id)]

    @staticmethod
    def get_smart_cards(
        user_id: int, exam_id: int, limit: int, db: Session = Depends(get_db)
    ) -> list[int]:
        stats = (
            db.query(Statistic.card_id, Statistic.mistakes_count)
            .filter(Statistic.user_id == user_id, Statistic.exam_id == exam_id)
            .order_by(Statistic.mistakes_count.desc())
            .limit(limit)
            .all()
        )

        return [stat.card_id for stat in stats]

    @staticmethod
    def smart_session_size(cards_count: int) -> int:
        if cards_count <= 1:
            return cards_count

        a = 1.0
        b = 10.0

        target_ratio = a * cards_count / (b + cards_count)
        session_size = round(cards_count * (1.5 - target_ratio))

        return max(1, session_size)
