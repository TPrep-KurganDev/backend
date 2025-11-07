from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

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
    request: ExamSessionStartRequest, db: Session = Depends(get_db)
) -> ExamSessionResponse:
    user = db.query(User).get(request.user_id)
    if not user:
        raise UserNotFound()

    exam = db.query(Exam).get(request.exam_id)
    if not exam:
        raise ExamNotFound()

    session = SessionFactory.create_session(user, exam, request.strategy, request.n, db)

    return session


@router.post("/{session_id}/answer")
def set_answer(session_id: int, question_id: int, value: bool) -> dict[str, str]:
    session = SessionFactory.get_session_by_id(session_id)
    if not session:
        raise SessionNotFound()

    session.set_answer(question_id, value)

    return {"status": "ok"}
