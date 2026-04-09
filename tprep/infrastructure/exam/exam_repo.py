from uuid import UUID

from fastapi import Depends
from sqlalchemy.orm import Session

from tprep.app.card_schemas import CardBase
from tprep.app.exam_schemas import ExamCreate
from tprep.infrastructure import Exam, UserExams, Card
from tprep.infrastructure.database import get_db
from tprep.infrastructure.exceptions.card_not_found import CardNotFound
from tprep.infrastructure.exceptions.exam_not_found import ExamNotFound
from tprep.infrastructure.exceptions.user_not_found import UserNotFound
from tprep.infrastructure.user.user_repo import UserRepo


class ExamRepo:
    @staticmethod
    def get_exam(exam_id: UUID, db: Session = Depends(get_db)) -> Exam:
        exam = db.query(Exam).filter(Exam.id == exam_id).first()
        if exam is None:
            raise ExamNotFound(f"Exam with id:{exam_id} not found")
        return exam

    @staticmethod
    def update_exam(
        exam_id: UUID, exam_data: ExamCreate, db: Session = Depends(get_db)
    ) -> Exam:
        exam = ExamRepo.get_exam(exam_id, db)

        update_data = exam_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(exam, key, value)

        db.commit()
        db.refresh(exam)
        return exam

    @staticmethod
    def add_exam(exam: Exam, creator_id: UUID, db: Session = Depends(get_db)) -> None:
        if not UserRepo.check_user_exists(creator_id, db):
            raise UserNotFound("User with specified creator id does not exist")

        db.add(exam)
        db.commit()
        db.refresh(exam)

    @staticmethod
    def get_exams_created_by_user(
        creator_id: UUID, db: Session = Depends(get_db)
    ) -> list[Exam]:
        if not UserRepo.check_user_exists(creator_id, db):
            raise UserNotFound("User with specified creator id does not exist")
        return db.query(Exam).filter(Exam.creator_id == creator_id).all()

    @staticmethod
    def get_exams_pinned_by_user(
        pinned_id: UUID, db: Session = Depends(get_db)
    ) -> list[Exam]:
        if not UserRepo.check_user_exists(pinned_id, db):
            raise UserNotFound("User with specified pinned id does not exist")
        return (
            db.query(Exam)
            .join(UserExams, Exam.id == UserExams.exam_id)
            .filter(UserExams.user_id == pinned_id)
            .all()
        )

    @staticmethod
    def delete_exam(exam_id: UUID, db: Session = Depends(get_db)) -> None:
        exam = ExamRepo.get_exam(exam_id, db)

        db.delete(exam)
        db.commit()

    @staticmethod
    def get_cards_by_exam_id(
        exam_id: UUID, db: Session = Depends(get_db)
    ) -> list[Card]:
        cards = db.query(Card).filter(Card.exam_id == exam_id).all()
        return cards

    @staticmethod
    def get_card(card_id: int, db: Session) -> Card:
        card = db.query(Card).filter(Card.card_id == card_id).first()
        if not card:
            raise CardNotFound(f"Card with id:{card_id} not found")
        return card

    @staticmethod
    def create_card(exam_id: UUID, db: Session = Depends(get_db)) -> Card:
        number = ExamRepo.count_next_number(exam_id, db)
        new_card = Card(number=number, exam_id=exam_id, question="", answer="")
        db.add(new_card)
        db.commit()
        db.refresh(new_card)
        return new_card

    @staticmethod
    def create_card_by_list(
        exam_id: UUID, cards_data: list[tuple[str, str]], db: Session
    ) -> list[Card]:
        cards = []
        for card_data in cards_data:
            question, answer = card_data
            number = ExamRepo.count_next_number(exam_id, db)
            new_card = Card(
                number=number, exam_id=exam_id, question=question, answer=answer
            )
            cards.append(new_card)
            db.add(new_card)
            db.commit()
            db.refresh(new_card)
        return cards

    @staticmethod
    def update_card(
        exam_id: UUID, card_id: int, card_data: CardBase, db: Session = Depends(get_db)
    ) -> Card:
        card = (
            db.query(Card)
            .filter(Card.card_id == card_id, Card.exam_id == exam_id)
            .first()
        )
        if not card:
            raise CardNotFound()
        update_data = card_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(card, key, value)

        db.commit()
        db.refresh(card)
        return card

    @staticmethod
    def delete_card(exam_id: UUID, card_id: int, db: Session = Depends(get_db)) -> None:
        card = (
            db.query(Card)
            .filter(Card.card_id == card_id, Card.exam_id == exam_id)
            .first()
        )
        db.delete(card)
        db.commit()

    @staticmethod
    def count_next_number(exam_id: UUID, db: Session) -> int:
        return len(db.query(Card).filter(Card.exam_id == exam_id).all()) + 1

    @staticmethod
    def user_can_edit_exam(user_id: UUID, exam_id: UUID, db: Session) -> bool:
        if UserRepo.check_that_user_is_creator(user_id, exam_id, db):
            return True

        editor_link = (
            db.query(UserExams)
            .filter(
                UserExams.user_id == user_id,
                UserExams.exam_id == exam_id,
                UserExams.rights == "editor",
            )
            .first()
        )
        return editor_link is not None

    @staticmethod
    def get_editor_ids(exam_id: UUID, db: Session) -> list[UUID]:
        editors = (
            db.query(UserExams)
            .filter(UserExams.exam_id == exam_id, UserExams.rights == "editor")
            .all()
        )
        return [editor.user_id for editor in editors]

    @staticmethod
    def user_can_view_exam(user_id: UUID, exam: Exam, db: Session) -> bool:
        if exam.scope != "personal":
            return True
        return ExamRepo.user_can_edit_exam(user_id, exam.id, db)

    @staticmethod
    def pin_exam(user_id: UUID, exam_id: UUID, db: Session = Depends(get_db)) -> None:
        pinned_exam = UserExams(user_id=user_id, exam_id=exam_id)
        db.query(UserExams)
        db.add(pinned_exam)
        db.commit()
        db.refresh(pinned_exam)

    @staticmethod
    def unpin_exam(user_id: UUID, exam_id: UUID, db: Session = Depends(get_db)) -> None:
        db.query(UserExams).filter(
            UserExams.user_id == user_id, UserExams.exam_id == exam_id
        ).delete()
        db.commit()

    @staticmethod
    def check_pinned_exam(
        user_id: UUID, exam_id: UUID, db: Session = Depends(get_db)
    ) -> bool:
        pinned_exam = (
            db.query(UserExams)
            .filter(UserExams.user_id == user_id, UserExams.exam_id == exam_id)
            .first()
        )
        if pinned_exam:
            return True
        return False
