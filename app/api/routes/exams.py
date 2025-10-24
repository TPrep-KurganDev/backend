from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from app.schemas import *
from infrastructure.exam.exam import Exam, UserPinnedExam, UserCreatedExam
from jose import jwt, JWTError

from infrastructure.exam.exam_repo import ExamRepo
from infrastructure.database import get_db
from config import SECRET_KEY, ALGORITHM
from infrastructure.exceptions.exam_not_found import ExamNotFound
from infrastructure.exceptions.user_is_not_creator import UserIsNotCreator
from infrastructure.user.user_repo import UserRepo

router = APIRouter(prefix="/exams", tags=["Exams"])


def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = int(payload.get("sub"))
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError as e:
        print(f"Authentication failed. Error: {e}")
        raise HTTPException(status_code=401, detail="Invalid or expired token")


@router.get("/pinned", response_model=List[ExamOut])
def get_pinned_exams(pinned_id: int = Query(None, description="Id of the user that pinned exam"),
                     db: Session = Depends(get_db), ):
    return ExamRepo.get_exams_pinned_by_user(pinned_id, db)


@router.get("/created", response_model=List[ExamOut])
def get_exams(
        creator_id: int = Query(None, description="Id of the user that created exam"),
        db: Session = Depends(get_db),
):
    return ExamRepo.get_exams_created_by_user(creator_id, db)


@router.post("/", response_model=ExamOut)
def create_exam(
        exam_data: ExamCreate,
        user_id: int = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    new_exam = Exam(title=exam_data.title)
    ExamRepo.add_exam(new_exam, user_id, db)
    return new_exam


@router.patch("/{examId}", response_model=ExamOut)
def update_exam(
        exam_id: int,
        exam_data: ExamCreate,
        user_id: int = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    if not UserRepo.check_that_user_is_creator(user_id, exam_id, db):
        raise UserIsNotCreator("User is not creator")

    return ExamRepo.update_exam(exam_id, exam_data, db)


@router.delete("/{examId}", status_code=204)
def delete_exam(
        exam_id: int,
        user_id: int = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    if not UserRepo.check_that_user_is_creator(user_id, exam_id, db):
        raise UserIsNotCreator("User is not creator")

    ExamRepo.delete_exam(exam_id, db)


@router.get("/{examId}", response_model=ExamOut)
def get_exam(exam_id: int, db: Session = Depends(get_db)):
    return ExamRepo.get_exam(exam_id, db)
