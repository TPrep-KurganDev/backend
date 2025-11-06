from fastapi import Header
from passlib.context import CryptContext
import datetime
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from jose import jwt, JWTError

from infrastructure.exceptions.invalid_authorization_header import (
    InvalidAuthorizationHeader,
)
from infrastructure.exceptions.invalid_or_expired_token import InvalidOrExpiredToken
from infrastructure.exceptions.user_not_found import UserNotFound


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(password: str, hash_: str):
    return pwd_context.verify(password, hash_)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
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


def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise InvalidAuthorizationHeader
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = int(payload.get("sub"))
        if user_id is None:
            raise InvalidOrExpiredToken
        return user_id
    except JWTError as e:
        print(f"Authentication failed. Error: {e}")
        raise InvalidOrExpiredToken
