from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from tprep.app.card_schemas import (
    CardBase,
    CardResponse,
    GenerateAnswersRequest,
    GenerateAnswersResponse,
    CardGenerationResult,
)
from tprep.infrastructure.exam.exam import Card
from tprep.infrastructure.authorization import get_current_user_id
from tprep.infrastructure.exam.exam_repo import ExamRepo
from tprep.infrastructure.database import get_db
from tprep.infrastructure.exceptions.card_not_found import CardNotFound
from tprep.infrastructure.exceptions.exam_has_no_cards import ExamHasNoCards
from tprep.infrastructure.exceptions.file_extension import FileExtension
from tprep.infrastructure.exceptions.user_is_not_creator import UserIsNotEditor
from tprep.infrastructure.user.user_repo import UserRepo
from tprep.infrastructure.parser.file_parser import FileParser
from tprep.domain.services.ai_answer_generator import AiAnswerGenerator


router = APIRouter(tags=["Cards"])


@router.post("/exams/{exam_id}/cards", response_model=CardResponse)
def create_card(
    exam_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
) -> Card:
    if not ExamRepo.user_can_edit_exam(user_id, exam_id, db):
        raise UserIsNotEditor("User has no rights to edit this exam")
    return ExamRepo.create_card(exam_id, db)


@router.post(
    "/exams/{exam_id}/cards/upload",
    response_model=list[CardResponse],
    description="Создает карточки из файла. Формат файла: вопрос1 | ответ1; вопрос2 | ответ2;",
)
async def create_cards_from_file(
    exam_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
    file: UploadFile = File(...),
) -> List[Card]:
    if not ExamRepo.user_can_edit_exam(user_id, exam_id, db):
        raise UserIsNotEditor("User has no rights to edit this exam")
    if not FileParser.check_extension(file.filename):
        raise FileExtension("Cant parse file with this extension")
    cards_data = await FileParser.parse_file(file)
    print(cards_data)
    return ExamRepo.create_card_by_list(exam_id, cards_data, db)


@router.get("/exams/{exam_id}/cards", response_model=List[CardResponse])
def get_cards_list(
    exam_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> List[Card]:
    exam = ExamRepo.get_exam(exam_id, db)
    if not ExamRepo.user_can_view_exam(user_id, exam, db):
        raise UserIsNotEditor("User has no rights to view this exam")
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
    exam_id: UUID,
    card_id: int,
    card_data: CardBase,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
) -> Card:
    if not ExamRepo.user_can_edit_exam(user_id, exam_id, db):
        raise UserIsNotEditor("User has no rights to edit this exam")
    return ExamRepo.update_card(exam_id, card_id, card_data, db)


@router.delete("/exams/{exam_id}/cards/{card_id}", status_code=204)
def delete_card(
    exam_id: UUID,
    card_id: int,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
) -> None:
    if not ExamRepo.user_can_edit_exam(user_id, exam_id, db):
        raise UserIsNotEditor("User has no rights to edit this exam")

    ExamRepo.delete_card(exam_id, card_id, db)


@router.post(
    "/exams/{exam_id}/cards/generate-answers",
    response_model=GenerateAnswersResponse,
    description="Generate AI answers for exam cards using OpenRouter AI",
)
def generate_answers(
    exam_id: int,
    request: GenerateAnswersRequest | None = None,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
) -> GenerateAnswersResponse:
    if not UserRepo.check_that_user_is_creator(user_id, exam_id, db):
        raise UserIsNotCreator("User is not creator")

    all_cards = ExamRepo.get_cards_by_exam_id(exam_id, db)

    if not all_cards:
        raise ExamHasNoCards("Exam has no cards")

    if request and request.card_ids is not None:
        cards = [c for c in all_cards if c.card_id in request.card_ids]
        found_ids = {c.card_id for c in cards}
        missing = set(request.card_ids) - found_ids
        if missing:
            raise CardNotFound(f"Cards not found in exam {exam_id}: {missing}")
    else:
        cards = all_cards

    ai_generator = AiAnswerGenerator()
    card_pairs = [(c.card_id, c.question) for c in cards]
    results = ai_generator.generate_answers_batch(card_pairs)

    card_lookup = {c.card_id: c for c in cards}
    response_cards: list[CardGenerationResult] = []
    successful = 0
    failed = 0

    for result in results:
        card = card_lookup[result.card_id]
        if result.success and result.answer is not None:
            successful += 1
        else:
            failed += 1

        response_cards.append(
            CardGenerationResult(
                card_id=card.card_id,
                number=card.number,
                question=card.question,
                answer=result.answer,
                success=result.success,
                error=result.error,
            )
        )

    return GenerateAnswersResponse(
        total=len(results),
        successful=successful,
        failed=failed,
        cards=response_cards,
    )
