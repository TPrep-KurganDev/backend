from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from app.card_schemas import CardBase
from app.exam_schemas import *
from infrastructure.exam.exam import Exam
from infrastructure.authorization import get_current_user_id
from infrastructure.exam.exam_repo import ExamRepo
from infrastructure.database import get_db
from infrastructure.exceptions.user_is_not_creator import UserIsNotCreator
from infrastructure.user.user_repo import UserRepo

router = APIRouter(prefix="/exams", tags=["Exams"])



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
        user_id: int = Depends(get_current_user_id),
        db: Session = Depends(get_db),
):
    new_exam = Exam(title=exam_data.title, creator_id=user_id)
    ExamRepo.add_exam(new_exam, user_id, db)
    return new_exam

@router.post("/{examId}/cards", response_model=CardBase)
def create_card(
        exam_id: int,
        db: Session = Depends(get_db),
        user_id: int = Depends(get_current_user_id)
):
    if not UserRepo.check_that_user_is_creator(user_id, exam_id, db):
        raise UserIsNotCreator("User is not creator")
    exam = ExamRepo.get_exam(exam_id, db)
    return ExamRepo.create_card(exam_id, db)

@router.patch("/{examId}/cards/{cardId}", response_model=CardBase)
def update_card(
        exam_id: int,
        card_id: int,
        card_data: CardBase,
        db: Session = Depends(get_db),
        user_id: int = Depends(get_current_user_id)
):
    if not UserRepo.check_that_user_is_creator(user_id, exam_id, db):
        raise UserIsNotCreator("User is not creator")
    exam = ExamRepo.get_exam(exam_id, db)
    return ExamRepo.update_card(exam_id, card_id, card_data, db)

@router.delete("/{examId}/cards/{cardId}", status_code=204)
def delete_card(
        exam_id: int,
        card_id: int,
        db: Session = Depends(get_db),
        user_id: int = Depends(get_current_user_id)
):
    if not UserRepo.check_that_user_is_creator(user_id, exam_id, db):
        raise UserIsNotCreator("User is not creator")

    ExamRepo.delete_card(exam_id, card_id, db)

@router.patch("/{examId}", response_model=ExamOut)
def update_exam(
        exam_id: int,
        exam_data: ExamCreate,
        user_id: int = Depends(get_current_user_id),
        db: Session = Depends(get_db),
):
    if not UserRepo.check_that_user_is_creator(user_id, exam_id, db):
        raise UserIsNotCreator("User is not creator")

    return ExamRepo.update_exam(exam_id, exam_data, db)


@router.delete("/{examId}", status_code=204)
def delete_exam(
        exam_id: int,
        user_id: int = Depends(get_current_user_id),
        db: Session = Depends(get_db),
):
    if not UserRepo.check_that_user_is_creator(user_id, exam_id, db):
        raise UserIsNotCreator("User is not creator")

    ExamRepo.delete_exam(exam_id, db)


@router.get("/{examId}", response_model=ExamOut)
def get_exam(exam_id: int, db: Session = Depends(get_db)):
    return ExamRepo.get_exam(exam_id, db)
