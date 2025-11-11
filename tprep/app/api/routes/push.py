from fastapi import APIRouter, Depends, HTTPException
from tprep.app.push_schemas import PushUpdate
from sqlalchemy.orm import Session
from tprep.infrastructure.database import get_db
from tprep.infrastructure.authorization import get_current_user_id
from tprep.infrastructure.user.user_repo import UserRepo

router = APIRouter()


@router.post("/push/register")
def register_push(
    data: PushUpdate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    if not user_id:
        raise HTTPException(status_code=401, detail="User not authenticated")

    UserRepo.register_push(user_id, data.push_key, endpoint=data.endpoint, db=db)
    return {"status": "ok"}


@router.post("/push/unregister")
def unregister_push(
    user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)
):
    UserRepo.unregister_push(user_id, db)
    return {"status": "ok"}
