from fastapi import APIRouter, Depends
from pydantic.v1 import EmailStr
from sqlalchemy.orm import Session

from tprep.app.user_schemas import UserOut
from tprep.infrastructure.database import get_db
from tprep.infrastructure.user.user import User
from tprep.infrastructure.user.user_repo import UserRepo

router = APIRouter(tags=["Users"])


@router.get("/users/{user_id}", response_model=UserOut)
def get_user_by_id(
        user_id: int,
        db: Session = Depends(get_db),
) -> User:
    return UserRepo.get_user_by_id(user_id, db)


@router.get("/users/{user_email}", response_model=UserOut)
def get_user_by_email(
        user_email: EmailStr,
        db: Session = Depends(get_db),
) -> User:
    return UserRepo.get_user_by_email(user_email, db)
