from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from app.schemas import *
from infrastructure.models import Exam, UserPinnedExam, UserCreatedExam
from jose import jwt, JWTError
from infrastructure.database import get_db
from config import SECRET_KEY, ALGORITHM

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


@router.get("/", response_model=List[ExamOut])
def get_exams(
    creator_id: Optional[int] = Query(None, description="ID пользователя, создавшего экзамен"),
    pinned_id: Optional[int] = Query(None, description="ID пользователя, закрепившего экзамен"),
    db: Session = Depends(get_db),
):
    if creator_id and pinned_id:
        raise HTTPException(status_code=400, detail="Нельзя указывать одновременно creatorId и pinnedId")

    if creator_id:
        exams = (
            db.query(Exam)
            .join(UserCreatedExam, Exam.id == UserCreatedExam.exam_id)
            .filter(UserCreatedExam.user_id == creator_id)
            .all()
        )
    elif pinned_id:
        exams = (
            db.query(Exam)
            .join(UserPinnedExam, Exam.id == UserPinnedExam.exam_id)
            .filter(UserPinnedExam.user_id == pinned_id)
            .all()
        )
    else:
        exams = db.query(Exam).all()

    return exams


@router.post("/", response_model=ExamOut)
def create_exam(
    exam_data: ExamCreate,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    new_exam = Exam(title=exam_data.title)
    db.add(new_exam)
    db.commit()
    db.refresh(new_exam)

    created_link = UserCreatedExam(user_id=user_id, exam_id=new_exam.id)
    db.add(created_link)
    db.commit()

    return new_exam



@router.patch("/{examId}", response_model=ExamOut)
def update_exam(
    exam_id: int,
    exam_data: ExamCreate,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    link = db.query(UserCreatedExam).filter(
        UserCreatedExam.exam_id == exam_id,
        UserCreatedExam.user_id == user_id
    ).first()
    if not link:
        raise HTTPException(status_code=403, detail="You are not the creator of this exam")

    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    update_data = exam_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(exam, key, value)

    db.commit()
    db.refresh(exam)
    return exam


@router.delete("/{examId}", status_code=204)
def delete_exam(
    exam_id: int,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    link = db.query(UserCreatedExam).filter(
        UserCreatedExam.exam_id == exam_id,
        UserCreatedExam.user_id == user_id
    ).first()
    if not link:
        raise HTTPException(status_code=403, detail="You are not the creator of this exam")

    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    db.delete(exam)
    db.commit()


@router.get("/{examId}", response_model=ExamOut)
def get_exam(exam_id: int, db: Session = Depends(get_db)):
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    return exam