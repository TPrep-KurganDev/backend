from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from tprep.infrastructure.authorization import get_current_user_id
from tprep.infrastructure.database import get_db
from tprep.domain.services.session_factory import SessionFactory
from tprep.app.session_schemas import ExamSessionResponse, ExamSessionStartRequest
from tprep.infrastructure.exceptions.session_not_found import SessionNotFound
from tprep.infrastructure.exceptions.user_not_found import UserNotFound
from tprep.infrastructure.exceptions.exam_not_found import ExamNotFound
from tprep.infrastructure.exam.exam import Exam
from tprep.infrastructure.user.user import User

router = APIRouter(prefix="/session", tags=["Session"])


@router.post("/", response_model=ExamSessionResponse)
def start_exam_session(
    request: ExamSessionStartRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
) -> ExamSessionResponse:
    user = db.query(User).get(user_id)
    if not user:
        raise UserNotFound()

    exam = db.query(Exam).get(request.exam_id)
    if not exam:
        raise ExamNotFound()

    session = SessionFactory.create_session(user, exam, request.strategy, request.n, db)

    return ExamSessionResponse.model_validate(session)


@router.get("/{session_id}", response_model=ExamSessionResponse)
def get_exam_session(session_id: str) -> ExamSessionResponse:
    session = SessionFactory.get_session_by_id(session_id)
    if session is None:
        raise SessionNotFound("Session not found")

    return ExamSessionResponse.model_validate(session)


@router.post("/{session_id}/answer")
def set_answer(
    session_id: str, question_id: int, value: bool, db: Session = Depends(get_db)
) -> dict[str, str]:
    session = SessionFactory.get_session_by_id(session_id)
    if session is None:
        raise SessionNotFound("Session not found")

    session.set_answer(question_id, value, db)

    return {"status": "ok"}
