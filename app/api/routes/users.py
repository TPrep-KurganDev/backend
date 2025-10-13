from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas import UserCreate, UserOut
from infrastructure.models import User
from passlib.context import CryptContext
from jose import jwt
from infrastructure.database import get_db
import datetime
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(password: str, hash_: str):
    return pwd_context.verify(password, hash_)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/register", response_model=UserOut)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(user.login == User.login).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = User(
        login=user.login,
        name=user.name,
        surname=user.surname,
        password_hash=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login")
def login_user(form_data: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(form_data.login == User.login).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Wrong login or password")

    token = create_access_token({"sub": user.login})
    return {"access_token": token, "token_type": "bearer"}
