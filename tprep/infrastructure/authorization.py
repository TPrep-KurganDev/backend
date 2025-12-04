from typing import cast

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
from tprep.infrastructure.exceptions.user_not_found import UserNotFound
from tprep.infrastructure import User
from tprep.infrastructure.user.user_repo import UserRepo

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


def hash_password(password: str) -> str:
    return cast(str, pwd_context.hash(password))


def verify_password(password: str, hash_: str) -> bool:
    return cast(bool, pwd_context.verify(password, hash_))


def create_access_token(data: TokenData) -> str:
    to_encode = data.model_dump()
    expire = datetime.datetime.utcnow() + datetime.timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    return cast(
        str, jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    )


def verify_refresh_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise UserNotFound
        return TokenData(sub=user_id)
    except JWTError:
        raise InvalidOrExpiredToken


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
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
