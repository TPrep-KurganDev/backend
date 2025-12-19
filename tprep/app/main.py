from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Callable, Coroutine

import uvicorn
from fastapi import FastAPI, Request, status, APIRouter
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from config import settings
from tprep.app.api.routes.auth import router as auth_router
from tprep.app.api.routes.exams import router as exams_router
from tprep.app.api.routes.cards import router as cards_router
from tprep.app.api.routes.session import router as session_router
from tprep.app.api.routes.users import router as users_router
from tprep.app.api.routes.push import router as push_router
from tprep.app.api.routes.notifications import router as notifications_router
from tprep.infrastructure.exceptions.UnexceptableStrategy import UnexceptableStrategy
from tprep.infrastructure.exceptions.card_not_found import CardNotFound
from tprep.infrastructure.exceptions.exam_has_no_cards import ExamHasNoCards
from tprep.infrastructure.exceptions.exam_not_found import ExamNotFound
from tprep.infrastructure.exceptions.file_decode import FileDecode
from tprep.infrastructure.exceptions.file_extension import FileExtension
from tprep.infrastructure.exceptions.file_parsing import FileParsing
from tprep.infrastructure.exceptions.invalid_authorization_header import (
    InvalidAuthorizationHeader,
)
from tprep.infrastructure.exceptions.invalid_or_expired_token import (
    InvalidOrExpiredToken,
)
from tprep.infrastructure.exceptions.question_not_in_session import QuestionNotInSession
from tprep.infrastructure.exceptions.session_not_found import SessionNotFound
from tprep.infrastructure.exceptions.user_already_exists import UserAlreadyExists
from tprep.infrastructure.exceptions.user_is_not_creator import UserIsNotCreator
from tprep.infrastructure.exceptions.user_not_found import UserNotFound
from tprep.infrastructure.exceptions.wrong_login_or_password import WrongLoginOrPassword
from tprep.infrastructure.exceptions.wrong_n_value import WrongNValue
from tprep.infrastructure import Base
from tprep.infrastructure.database import engine

APP_ERRORS = {
    Exception: status.HTTP_500_INTERNAL_SERVER_ERROR,
    ExamNotFound: status.HTTP_404_NOT_FOUND,
    CardNotFound: status.HTTP_404_NOT_FOUND,
    SessionNotFound: status.HTTP_404_NOT_FOUND,
    WrongNValue: status.HTTP_422_UNPROCESSABLE_ENTITY,
    FileExtension: status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
    FileDecode: status.HTTP_400_BAD_REQUEST,
    FileParsing: status.HTTP_400_BAD_REQUEST,
    ExamHasNoCards: status.HTTP_422_UNPROCESSABLE_ENTITY,
    QuestionNotInSession: status.HTTP_400_BAD_REQUEST,
    UserAlreadyExists: status.HTTP_409_CONFLICT,
    UserIsNotCreator: status.HTTP_403_FORBIDDEN,
    UserNotFound: status.HTTP_404_NOT_FOUND,
    WrongLoginOrPassword: status.HTTP_401_UNAUTHORIZED,
    InvalidOrExpiredToken: status.HTTP_401_UNAUTHORIZED,
    InvalidAuthorizationHeader: status.HTTP_401_UNAUTHORIZED,
    UnexceptableStrategy: status.HTTP_422_UNPROCESSABLE_ENTITY,
}


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
    Base.metadata.create_all(bind=engine)

    #    clear_db()
    #    db = SessionLocal()
    #   create_mock_users(db)
    #    db.close()
    yield


def add_exception_handlers(
    app: FastAPI, api_exceptions: dict[type[Exception], int]
) -> None:
    def make_handler(
        exc_type: type[Exception], status_code: int
    ) -> Callable[[Request, Exception], Coroutine[Any, Any, JSONResponse]]:
        async def handler(request: Request, exc: Exception) -> JSONResponse:
            return JSONResponse(
                status_code=status_code,
                content={
                    "error": exc_type.__name__,
                    "message": getattr(exc, "message", str(exc)),
                },
            )

        return handler

    for exc_type, status_code in api_exceptions.items():
        app.add_exception_handler(exc_type, make_handler(exc_type, status_code))


app = FastAPI(
    title="Backend API",
    version="0.1.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

add_exception_handlers(app, APP_ERRORS)
api_router = APIRouter(prefix="/api")
api_router.include_router(auth_router)
api_router.include_router(exams_router)
api_router.include_router(cards_router)
api_router.include_router(session_router)
api_router.include_router(users_router)
api_router.include_router(push_router)
api_router.include_router(notifications_router)


@api_router.get("/health", tags=["Health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
