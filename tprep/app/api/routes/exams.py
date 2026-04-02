from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException
from requests import HTTPError
from requests.exceptions import RequestException
from sqlalchemy.orm import Session

from tprep.infrastructure.exam.exam import Card, Exam, UserExams
from tprep.infrastructure.authorization import get_current_user_id
from tprep.infrastructure.exam.exam_repo import ExamRepo
from tprep.infrastructure.database import get_db
from tprep.infrastructure.exceptions.user_is_not_creator import UserIsNotEditor
from tprep.infrastructure.exceptions.exam_not_found import ExamNotFound
from tprep.infrastructure.notification.notification_repo import NotificationRepo
from tprep.infrastructure.user.user_repo import UserRepo
from tprep.infrastructure.ocr import (
    OcrConfigurationError,
    OcrParseError,
    cards_from_image,
)

from tprep.app.card_schemas import CardResponse
from tprep.app.exam_schemas import (
    ExamOut,
    ExamCreate,
    ExamPinStatus,
    ExamRightsResponse,
)
from tprep.app.ocr_schemas import OcrRequest

router = APIRouter(tags=["Exams"])


@router.get("/exams/pinned", response_model=List[ExamOut])
def get_pinned_exams(
    pinned_id: UUID = Query(None, description="Id of the user that pinned exam"),
    db: Session = Depends(get_db),
) -> list[Exam]:
    return ExamRepo.get_exams_pinned_by_user(pinned_id, db)


@router.get("/exams/created", response_model=List[ExamOut])
def get_exams(
    creator_id: UUID = Query(None, description="Id of the user that created exam"),
    db: Session = Depends(get_db),
) -> list[Exam]:
    return ExamRepo.get_exams_created_by_user(creator_id, db)


@router.post("/exams", response_model=ExamOut)
def create_exam(
    exam_data: ExamCreate,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> Exam:
    new_exam = Exam(title=exam_data.title, scope=exam_data.scope, creator_id=user_id)
    ExamRepo.add_exam(new_exam, user_id, db)
    return new_exam


@router.patch("/exams/{exam_id}", response_model=ExamOut)
def update_exam(
    exam_id: UUID,
    exam_data: ExamCreate,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> Exam:
    if not ExamRepo.user_can_edit_exam(user_id, exam_id, db):
        raise UserIsNotEditor("User has no rights to edit this exam")

    return ExamRepo.update_exam(exam_id, exam_data, db)


@router.delete("/exams/{exam_id}", status_code=204)
def delete_exam(
    exam_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> None:
    if not UserRepo.check_that_user_is_creator(user_id, exam_id, db):
        raise UserIsNotEditor("User is not creator")

    ExamRepo.delete_exam(exam_id, db)


@router.get("/exams/{exam_id}", response_model=ExamOut)
def get_exam(
    exam_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> Exam:
    exam = ExamRepo.get_exam(exam_id, db)
    if not ExamRepo.user_can_view_exam(user_id, exam, db):
        raise UserIsNotEditor("User has no rights to view this exam")
    return exam


@router.post("/exams/{exam_id}/pin", status_code=204)
def pin_exam(
    exam_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> None:
    NotificationRepo.create_notification(user_id, exam_id, db)
    ExamRepo.pin_exam(user_id, exam_id, db)


@router.post("/exams/{exam_id}/unpin", status_code=204)
def unpin_exam(
    exam_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> None:
    NotificationRepo.delete_notification(user_id, exam_id, db)
    ExamRepo.unpin_exam(user_id, exam_id, db)


@router.get("/exams/{exam_id}/check_pinning", response_model=ExamPinStatus)
def check_pinned_exam(
    exam_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> bool:
    return ExamRepo.check_pinned_exam(user_id, exam_id, db)


@router.post("/exams/{exam_id}/rights", status_code=204)
def grant_editor_rights(
    exam_id: UUID,
    target_user_id: UUID = Query(..., alias="user_id"),
    author_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> None:
    if not ExamRepo.user_can_edit_exam(author_id, exam_id, db):
        raise UserIsNotEditor("User has no rights to manage exam rights")

    if not UserRepo.check_user_exists(target_user_id, db):
        raise HTTPException(status_code=404, detail="Target user not found")

    link = (
        db.query(UserExams)
        .filter(
            UserExams.user_id == target_user_id,
            UserExams.exam_id == exam_id,
        )
        .first()
    )

    if link:
        link.rights = "editor"
    else:
        link = UserExams(
            user_id=target_user_id,
            exam_id=exam_id,
            rights="editor",
            is_pinned=False,
        )
        db.add(link)

    db.commit()


@router.patch("/exams/{exam_id}/rights", response_model=ExamRightsResponse)
def change_user_rights(
    exam_id: UUID,
    target_user_id: UUID = Query(..., alias="user_id"),
    rights: str = Query(..., description="New rights: editor or viewer"),
    author_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> ExamRightsResponse:
    if rights not in {"editor", "viewer"}:
        raise HTTPException(status_code=400, detail="Invalid rights value")

    if not ExamRepo.user_can_edit_exam(author_id, exam_id, db):
        raise UserIsNotEditor("User has no rights to manage exam rights")

    link = (
        db.query(UserExams)
        .filter(
            UserExams.user_id == target_user_id,
            UserExams.exam_id == exam_id,
        )
        .first()
    )

    if not link:
        link = UserExams(
            user_id=target_user_id,
            exam_id=exam_id,
            rights=rights,
            is_pinned=False,
        )
        db.add(link)
    else:
        link.rights = rights

    db.commit()

    editor_ids = ExamRepo.get_editor_ids(exam_id, db)
    return ExamRightsResponse(user_id=editor_ids)


@router.delete("/exams/{exam_id}/rights", status_code=204)
def revoke_user_rights(
    exam_id: UUID,
    target_user_id: UUID = Query(..., alias="user_id"),
    author_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> None:
    if not ExamRepo.user_can_edit_exam(author_id, exam_id, db):
        raise UserIsNotEditor("User has no rights to manage exam rights")

    (
        db.query(UserExams)
        .filter(
            UserExams.user_id == target_user_id,
            UserExams.exam_id == exam_id,
        )
        .delete()
    )
    db.commit()


@router.get("/exams/{exam_id}/rights", response_model=ExamRightsResponse)
def get_exam_editors(
    exam_id: UUID,
    requester_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> ExamRightsResponse:
    if not ExamRepo.user_can_edit_exam(requester_id, exam_id, db):
        raise UserIsNotEditor(
            "Only exam creator or editors can view rights information"
        )

    editor_ids = ExamRepo.get_editor_ids(exam_id, db)
    return ExamRightsResponse(user_id=editor_ids)


@router.post("/exams/{exam_id}/ocr", response_model=list[CardResponse])
def ocr_create_cards(
    exam_id: UUID,
    payload: OcrRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> list[Card]:
    if not ExamRepo.user_can_edit_exam(user_id, exam_id, db):
        raise UserIsNotEditor("User has no rights to edit this exam")

    ExamRepo.get_exam(exam_id, db)

    try:
        cards_data = cards_from_image(payload.image_name)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Image file not found") from exc
    except OcrParseError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except OSError as exc:
        raise HTTPException(status_code=400, detail="Cannot read image") from exc
    except OcrConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail="OCR provider returned an error",
        ) from exc
    except RequestException as exc:
        raise HTTPException(
            status_code=502,
            detail="OCR service request failed",
        ) from exc

    if not cards_data:
        raise HTTPException(
            status_code=400,
            detail="No cards could be parsed from the image",
        )

    return ExamRepo.create_card_by_list(exam_id, cards_data, db)
