from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from tprep.app.api.routes.auth import router as api_router
from tprep.app.api.routes.exams import router as exams_router
from tprep.app.api.routes.session import router as session_router
from tprep.infrastructure.exceptions.UnexceptableStrategy import UnexceptableStrategy
from tprep.infrastructure.exceptions.card_not_found import CardNotFound
from tprep.infrastructure.exceptions.exam_has_no_cards import ExamHasNoCards
from tprep.infrastructure.exceptions.exam_not_found import ExamNotFound
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
from tprep.infrastructure.models import Base
from tprep.infrastructure.database import engine

APP_ERRORS = {
    Exception: status.HTTP_500_INTERNAL_SERVER_ERROR,
    ExamNotFound: status.HTTP_404_NOT_FOUND,
    CardNotFound: status.HTTP_404_NOT_FOUND,
    SessionNotFound: status.HTTP_404_NOT_FOUND,
    WrongNValue: status.HTTP_422_UNPROCESSABLE_ENTITY,
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
    for exc_type, status_code in api_exceptions.items():

        async def handler(request: Request, exc: exc_type):  # type: ignore
            return JSONResponse(
                status_code=status_code,
                content={
                    "error": exc_type.__name__,
                    "message": getattr(exc, "message", str(exc)),
                },
            )

        app.add_exception_handler(exc_type, handler)


app = FastAPI(
    title="Backend API",
    version="0.1.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

origins = [
    "http://localhost:5173",  # Vite
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

add_exception_handlers(app, APP_ERRORS)
app.include_router(api_router, prefix="/api")
app.include_router(exams_router, prefix="/api")
app.include_router(session_router, prefix="/api")


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
