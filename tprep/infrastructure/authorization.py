from typing import cast
from uuid import UUID

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
import datetime

from sqlalchemy.orm import Session

from config import settings
from jose import jwt, JWTError

from tprep.app.authorization_schemas import TokenData
from tprep.infrastructure.database import get_db
from tprep.infrastructure.exceptions.invalid_or_expired_token import (
    InvalidOrExpiredToken,
)
from tprep.infrastructure import User
from tprep.infrastructure.user.user_repo import UserRepo

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

JWT_PURPOSE_ACCESS = "access"
JWT_PURPOSE_REFRESH = "refresh"


def hash_password(password: str) -> str:
    return cast(str, pwd_context.hash(password))


def verify_password(password: str, hash_: str) -> bool:
    return cast(bool, pwd_context.verify(password, hash_))


def create_access_token(data: TokenData) -> str:
    to_encode = data.model_dump(exclude_none=True)
    to_encode["purpose"] = JWT_PURPOSE_ACCESS
    expire = datetime.datetime.utcnow() + datetime.timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    return cast(
        str, jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    )


def create_refresh_token(data: TokenData) -> str:
    expire = datetime.datetime.utcnow() + datetime.timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    to_encode: dict[str, str | datetime.datetime] = {
        "sub": data.sub,
        "purpose": JWT_PURPOSE_REFRESH,
        "exp": expire,
    }
    if data.login is not None:
        to_encode["login"] = data.login
    return cast(
        str, jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    )


def verify_refresh_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        if payload.get("purpose") != JWT_PURPOSE_REFRESH:
            raise InvalidOrExpiredToken
        user_id = payload.get("sub")
        if user_id is None:
            raise InvalidOrExpiredToken
        login = payload.get("login")
        return TokenData(sub=str(user_id), login=login if login is not None else None)
    except JWTError:
        raise InvalidOrExpiredToken


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    user_id = get_current_user_id(token)
    return UserRepo.get_user_by_id(user_id, db)


def get_current_user_id(token: str = Depends(oauth2_scheme)) -> UUID:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        if payload.get("purpose") == JWT_PURPOSE_REFRESH:
            raise InvalidOrExpiredToken
        sub = payload.get("sub")
        if sub is None:
            raise InvalidOrExpiredToken
        return UUID(sub)

    except JWTError as e:
        print(f"Authentication failed. Error: {e}")
        raise InvalidOrExpiredToken
