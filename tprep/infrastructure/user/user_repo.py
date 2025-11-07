from fastapi import Depends
from pydantic import EmailStr
from sqlalchemy.orm import Session

from tprep.infrastructure.database import get_db
from tprep.infrastructure.exam.exam import Exam
from tprep.infrastructure.exceptions.user_not_found import UserNotFound
from tprep.infrastructure.user.user import User


class UserRepo:
    @staticmethod
    def check_user_exists(user_id: int, db: Session = Depends(get_db)) -> bool:
        user = db.query(User).filter(User.id == user_id).first()
        return bool(user)

    @staticmethod
    def check_that_user_is_creator(
        user_id: int, exam_id: int, db: Session = Depends(get_db)
    ) -> bool:
        link = (
            db.query(Exam)
            .filter(Exam.id == exam_id, Exam.creator_id == user_id)
            .first()
        )
        return bool(link)

    @staticmethod
    def get_user_by_email(email: EmailStr, db: Session = Depends(get_db)) -> User:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise UserNotFound
        return user

    @staticmethod
    def register_user(user: User, db: Session = Depends(get_db)) -> User:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
