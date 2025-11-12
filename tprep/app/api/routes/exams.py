from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from tprep.infrastructure.exam.exam import Exam, Card
from tprep.infrastructure.authorization import get_current_user_id
from tprep.infrastructure.exam.exam_repo import ExamRepo
from tprep.infrastructure.database import get_db
from tprep.infrastructure.exceptions.user_is_not_creator import UserIsNotCreator
from tprep.infrastructure.user.user_repo import UserRepo

from tprep.app.exam_schemas import ExamOut, ExamCreate
from tprep.app.card_schemas import CardBase, CardResponse

router = APIRouter(tags=["Exams", "Cards"])


@router.get("/exams/pinned", response_model=List[ExamOut])
def get_pinned_exams(
    pinned_id: int = Query(None, description="Id of the user that pinned exam"),
    db: Session = Depends(get_db),
) -> list[Exam]:
    return ExamRepo.get_exams_pinned_by_user(pinned_id, db)


@router.get("/exams/created", response_model=List[ExamOut])
def get_exams(
    creator_id: int = Query(None, description="Id of the user that created exam"),
    db: Session = Depends(get_db),
) -> list[Exam]:
    return ExamRepo.get_exams_created_by_user(creator_id, db)


@router.post("/exams/", response_model=ExamOut)
def create_exam(
    exam_data: ExamCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> Exam:
    new_exam = Exam(title=exam_data.title, creator_id=user_id)
    ExamRepo.add_exam(new_exam, user_id, db)
    return new_exam


@router.post("/exams/{exam_id}/cards", response_model=CardResponse)
def create_card(
    exam_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
) -> Card:
    if not UserRepo.check_that_user_is_creator(user_id, exam_id, db):
        raise UserIsNotCreator("User is not creator")
    return ExamRepo.create_card(exam_id, db)


@router.get("/exams/{exam_id}/cards", response_model=List[CardResponse])
def get_cards_list(
    exam_id: int,
    db: Session = Depends(get_db)
) -> List[Card]:
    cards = ExamRepo.get_cards_by_exam_id(exam_id, db)
    return cards

@router.get("/cards/{card_id}", response_model=CardBase)
def get_card(
        card_id: int,
        db: Session = Depends(get_db),
) -> Card:
    return ExamRepo.get_card(card_id, db)


@router.patch("/exams/{exam_id}/cards/{card_id}", response_model=CardBase)
def update_card(
    exam_id: int,
    card_id: int,
    card_data: CardBase,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
) -> Card:
    if not UserRepo.check_that_user_is_creator(user_id, exam_id, db):
        raise UserIsNotCreator("User is not creator")
    return ExamRepo.update_card(exam_id, card_id, card_data, db)


@router.delete("/exams/{exam_id}/cards/{card_id}", status_code=204)
def delete_card(
    exam_id: int,
    card_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
) -> None:
    if not UserRepo.check_that_user_is_creator(user_id, exam_id, db):
        raise UserIsNotCreator("User is not creator")

    ExamRepo.delete_card(exam_id, card_id, db)


@router.patch("/exams/{exam_id}", response_model=ExamOut)
def update_exam(
    exam_id: int,
    exam_data: ExamCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> Exam:
    if not UserRepo.check_that_user_is_creator(user_id, exam_id, db):
        raise UserIsNotCreator("User is not creator")

    return ExamRepo.update_exam(exam_id, exam_data, db)


@router.delete("/exams/{exam_id}", status_code=204)
def delete_exam(
    exam_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> None:
    if not UserRepo.check_that_user_is_creator(user_id, exam_id, db):
        raise UserIsNotCreator("User is not creator")

    ExamRepo.delete_exam(exam_id, db)


@router.get("/exams/{exam_id}", response_model=ExamOut)
def get_exam(exam_id: int, db: Session = Depends(get_db)) -> Exam:
    return ExamRepo.get_exam(exam_id, db)
