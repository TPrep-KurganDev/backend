from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from config import settings
from tprep.app.authorization_schemas import (
    Token,
    RefreshRequest,
    AccessTokenResponse,
    TokenData,
)
from tprep.app.user_schemas import UserCreate, UserOut, UserLogin
from tprep.infrastructure.authorization import (
    hash_password,
    create_access_token,
    verify_password,
    verify_refresh_token,
)
from tprep.infrastructure.exceptions.user_already_exists import UserAlreadyExists
from tprep.infrastructure.exceptions.user_not_found import UserNotFound
from tprep.infrastructure.exceptions.wrong_login_or_password import WrongLoginOrPassword
from tprep.infrastructure.user.user import User
from tprep.infrastructure.database import get_db
from tprep.infrastructure.user.user_repo import UserRepo

router = APIRouter(tags=["Auth"])


@router.post("/auth/register", response_model=UserOut)
def register_user(user: UserCreate, db: Session = Depends(get_db)) -> User:
    try:
        UserRepo.get_user_by_email(user.email, db)
    except UserNotFound:
        new_user = User(
            email=user.email,
            user_name=user.user_name,
            password_hash=hash_password(user.password),
        )
        return UserRepo.register_user(new_user, db)
    else:
        raise UserAlreadyExists


@router.post("/auth/login", response_model=Token)
def login_user(userLogin: UserLogin, db: Session = Depends(get_db)) -> Token:
    try:
        user = UserRepo.get_user_by_email(userLogin.email, db)
    except UserNotFound:
        raise WrongLoginOrPassword
    if not verify_password(userLogin.password, user.password_hash):
        raise WrongLoginOrPassword

    token_data = TokenData(sub=str(user.id), login=user.user_name)
    access_token = create_access_token(token_data)
    UserRepo.update_user_token(user.id, access_token, db)

    return Token(user_id=user.id, access_token=access_token, token_type="bearer")


@router.post("/auth/refresh", response_model=AccessTokenResponse)
def refresh_access_token(request: RefreshRequest) -> AccessTokenResponse:
    token_data = verify_refresh_token(request.refreshToken)
    access_token = create_access_token(token_data)
    UserRepo.update_user_token(int(token_data.sub), access_token)

    return AccessTokenResponse(
        accessToken=access_token,
        expiresIn=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        token_type="bearer",
    )
