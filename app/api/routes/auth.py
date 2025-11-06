from fastapi import APIRouter
from app.user_schemas import *
from app.authorization_schemas import *
from infrastructure.exceptions.user_already_exists import UserAlreadyExists
from infrastructure.exceptions.wrong_login_or_password import WrongLoginOrPassword
from infrastructure.authorization import *

router = APIRouter()

@router.post("/auth/register", response_model=UserOut)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        UserRepo.get_user_by_email(user.email, db)
    except UserNotFound:
        new_user = User(
            email=user.email,
            user_name=user.user_name,
            password_hash=hash_password(user.password)
        )

        return UserRepo.register_user(new_user, db)
    else:
        raise UserAlreadyExists


@router.post("/auth/login", response_model=Token)
def login_user(body: LoginRequest, db: Session = Depends(get_db)):
    try:
        user = UserRepo.get_user_by_email(body.email, db)
    except UserNotFound:
        raise WrongLoginOrPassword
    if not verify_password(body.password, user.password_hash):
        raise WrongLoginOrPassword

    token = create_access_token({"sub": str(user.id)})
    UserRepo.update_user_token(user.id, token, db)

    return Token(
        access_token=token,
        token_type="bearer"
    )


@router.post("/auth/refresh", response_model=AccessTokenResponse)
def refresh_access_token(request: RefreshRequest):
    token_data = verify_refresh_token(request.refreshToken)

    access_token = create_access_token({"sub": str(token_data["sub"])})
    UserRepo.update_user_token(int(token_data["sub"]), access_token)

    return AccessTokenResponse(
        accessToken=access_token,
        expiresIn=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        token_type= "bearer"
    )
