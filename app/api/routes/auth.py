from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas import *
from infrastructure.models import User
from passlib.context import CryptContext
from jose import jwt, JWTError
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


def verify_refresh_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        return {"sub": str(user_id)}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")


@router.post("/auth/register", response_model=UserOut)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(user.email == User.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = User(
        email=user.email,
        user_name = user.user_name,
        password_hash=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/auth/login", response_model=Token)
def login_user(form_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.email).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Wrong login or password")

    token = create_access_token({"sub": str(user.id)})
    return Token(
        access_token=token,
        token_type="bearer"
    )


@router.post("/auth/refresh", response_model=AccessTokenResponse)
def refresh_access_token(request: RefreshRequest):
    token_data = verify_refresh_token(request.refreshToken)

    access_token = create_access_token({"sub": str(token_data["sub"])})

    return AccessTokenResponse(
        accessToken=access_token,
        expiresIn=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        token_type= "bearer"
    )
