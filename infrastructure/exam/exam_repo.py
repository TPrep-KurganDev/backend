from fastapi import Depends
from sqlalchemy.orm import Session

from app.exam_schemas import ExamCreate
from infrastructure.exam.exam import Exam, UserPinnedExam
from infrastructure.database import get_db
from infrastructure.exceptions.exam_not_found import ExamNotFound
from infrastructure.exceptions.user_not_found import UserNotFound
from infrastructure.user.user_repo import UserRepo


class ExamRepo:
    @staticmethod
    def get_exam(exam_id: int, db: Session = Depends(get_db)) -> type[Exam] | None:
        exam = db.query(Exam).filter(Exam.id == exam_id).first()
        if not exam:
            raise ExamNotFound
        return exam

    @staticmethod
    def update_exam(exam_id: int, exam_data: ExamCreate, db: Session = Depends(get_db)) -> type[Exam]:
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
    def get_exams_created_by_user(creator_id: int, db: Session = Depends(get_db)) -> list[type[Exam]]:
        if not UserRepo.check_user_exists(creator_id, db):
            raise UserNotFound("User with specified creator id does not exist")
        return (
            db.query(Exam)
            .filter(Exam.creator_id == creator_id)
            .all()
        )

    @staticmethod
    def get_exams_pinned_by_user(pinned_id: int, db: Session = Depends(get_db)) -> list[type[Exam]]:
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
