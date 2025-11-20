from typing import List
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from tprep.app.card_schemas import CardBase, CardResponse
from tprep.infrastructure.exam.exam import Card
from tprep.infrastructure.authorization import get_current_user_id
from tprep.infrastructure.exam.exam_repo import ExamRepo
from tprep.infrastructure.database import get_db
from tprep.infrastructure.exceptions.file_extension import FileExtension
from tprep.infrastructure.exceptions.user_is_not_creator import UserIsNotCreator
from tprep.infrastructure.user.user_repo import UserRepo
from tprep.infrastructure.parser.file_parser import FileParser


router = APIRouter(tags=["Cards"])


@router.post("/exams/{exam_id}/cards", response_model=CardResponse)
def create_card(
    exam_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
) -> Card:
    if not UserRepo.check_that_user_is_creator(user_id, exam_id, db):
        raise UserIsNotCreator("User is not creator")
    return ExamRepo.create_card(exam_id, db)


@router.post("/exams/{exam_id}/cards/upload", response_model=list[CardResponse], description="Создает карточки из файла. Формат файла: вопрос1 | ответ1; вопрос2 | ответ2;")
async def create_cards_from_file(
    exam_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
    file: UploadFile = File(...),
) -> List[Card]:
    if not UserRepo.check_that_user_is_creator(user_id, exam_id, db):
        raise UserIsNotCreator("User is not creator")
    if not FileParser.check_extension(file.filename):
        raise FileExtension("Cant parse file with this extension")
    cards_data = await FileParser.parse_file(file)
    print(cards_data)
    return ExamRepo.create_card_by_list(exam_id, cards_data, db)


@router.get("/exams/{exam_id}/cards", response_model=List[CardResponse])
def get_cards_list(exam_id: int, db: Session = Depends(get_db)) -> List[Card]:
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
