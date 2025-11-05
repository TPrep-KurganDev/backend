from fastapi import Header, Depends
from passlib.context import CryptContext
import datetime

from sqlalchemy.orm import Session

from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from jose import jwt, JWTError

from infrastructure.database import get_db
from infrastructure.exceptions.invalid_authorization_header import InvalidAuthorizationHeader
from infrastructure.exceptions.invalid_or_expired_token import InvalidOrExpiredToken
from infrastructure.exceptions.user_not_found import UserNotFound
from infrastructure.user.user import User
from infrastructure.user.user_repo import UserRepo

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
            raise UserNotFound
        return {"sub": str(user_id)}
    except JWTError:
        raise InvalidOrExpiredToken



def get_current_user(
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    if not authorization.startswith("Bearer "):
        raise InvalidAuthorizationHeader
    token = authorization.split(" ")[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = int(payload.get("sub"))
        if user_id is None:
            raise InvalidOrExpiredToken

        user = UserRepo.get_user_by_id_and_token(user_id, token, db)
        return user

    except JWTError as e:
        print(f"Authentication failed. Error: {e}")
        raise InvalidOrExpiredToken


def get_current_user_id(current_user: User = Depends(get_current_user)) -> int:
    return current_user.id