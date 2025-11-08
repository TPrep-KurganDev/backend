from fastapi import Depends
from sqlalchemy.orm import Session

from tprep.app.exam_schemas import ExamCreate
from tprep.infrastructure.exam.exam import Exam, UserPinnedExam
from tprep.infrastructure.database import get_db
from tprep.infrastructure.exceptions.exam_not_found import ExamNotFound
from tprep.infrastructure.exceptions.user_not_found import UserNotFound
from tprep.infrastructure.user.user_repo import UserRepo


class ExamRepo:
    @staticmethod
    def get_exam(exam_id: int, db: Session = Depends(get_db)) -> Exam:
        exam = db.query(Exam).filter(Exam.id == exam_id).first()
        if exam is None:
            raise ExamNotFound
        return exam

    @staticmethod
    def update_exam(
        exam_id: int, exam_data: ExamCreate, db: Session = Depends(get_db)
    ) -> Exam:
        exam = ExamRepo.get_exam(exam_id, db)

        update_data = exam_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(exam, key, value)

        db.commit()
        db.refresh(exam)
        return exam

    @staticmethod
    def add_exam(exam: Exam, creator_id: int, db: Session = Depends(get_db)) -> None:
        if not UserRepo.check_user_exists(creator_id, db):
            raise UserNotFound("User with specified creator id does not exist")

        db.add(exam)
        db.commit()
        db.refresh(exam)

    @staticmethod
    def get_exams_created_by_user(
        creator_id: int, db: Session = Depends(get_db)
    ) -> list[Exam]:
        if not UserRepo.check_user_exists(creator_id, db):
            raise UserNotFound("User with specified creator id does not exist")
        return db.query(Exam).filter(Exam.creator_id == creator_id).all()

    @staticmethod
    def get_exams_pinned_by_user(
        pinned_id: int, db: Session = Depends(get_db)
    ) -> list[Exam]:
        if not UserRepo.check_user_exists(pinned_id, db):
            raise UserNotFound("User with specified pinned id does not exist")
        return (
            db.query(Exam)
            .join(UserPinnedExam, Exam.id == UserPinnedExam.exam_id)
            .filter(UserPinnedExam.user_id == pinned_id)
            .all()
        )

    @staticmethod
    def delete_exam(exam_id: int, db: Session = Depends(get_db)) -> None:
        exam = ExamRepo.get_exam(exam_id, db)

        db.delete(exam)
        db.commit()

    @staticmethod
    def get_card(exam_id: int, card_id: int, db: Session) -> Card:
        card = db.query(Card).filter(Card.card_id == card_id, Card.exam_id == exam_id).first()
        if not card:
            raise CardNotFound()
        return card

    @staticmethod
    def create_card(exam_id: int, db: Session = Depends(get_db)) -> Card:
        new_card = Card(exam_id=exam_id, question="", answer="")
        db.add(new_card)
        db.commit()
        db.refresh(new_card)
        return new_card

    @staticmethod
    def update_card(exam_id: int, card_id: int, card_data: CardBase, db: Session = Depends(get_db)) -> Card:
        card = db.query(Card).filter(Card.card_id == card_id, Card.exam_id == exam_id).first()
        if not card:
            raise CardNotFound()
        update_data = card_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(card, key, value)

        db.commit()
        db.refresh(card)
        return card

    @staticmethod
    def delete_card(exam_id:int, card_id: int, db: Session = Depends(get_db)) -> None:
        card = db.query(Card).filter(card_id=card_id, exam_id=exam_id).first()
        db.delete(card)
        db.commit()