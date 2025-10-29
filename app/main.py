from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from app.api.routes.auth import router as api_router
from app.api.routes.exams import router as exams_router
from infrastructure.exceptions.exam_not_found import ExamNotFound
from infrastructure.exceptions.invalid_authorization_header import InvalidAuthorizationHeader
from infrastructure.exceptions.invalid_or_expired_token import InvalidOrExpiredToken
from infrastructure.exceptions.user_already_exists import UserAlreadyExists
from infrastructure.exceptions.user_is_not_creator import UserIsNotCreator
from infrastructure.exceptions.user_not_found import UserNotFound
from infrastructure.exceptions.wrong_login_or_password import WrongLoginOrPassword
from infrastructure.models import Base
from infrastructure.database import engine, SessionLocal
from mocks.mock_users import create_mock_users
from helpers.clear_db import clear_db

APP_ERRORS = {
    Exception: status.HTTP_500_INTERNAL_SERVER_ERROR,
    ExamNotFound: status.HTTP_404_NOT_FOUND,
    UserAlreadyExists: status.HTTP_409_CONFLICT,
    UserIsNotCreator: status.HTTP_403_FORBIDDEN,
    UserNotFound: status.HTTP_404_NOT_FOUND,
    WrongLoginOrPassword: status.HTTP_401_UNAUTHORIZED,
    InvalidOrExpiredToken: status.HTTP_401_UNAUTHORIZED,
    InvalidAuthorizationHeader: status.HTTP_401_UNAUTHORIZED,
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)

    clear_db()
    db = SessionLocal()
    create_mock_users(db)
    db.close()
    yield

def add_exception_handlers(app: FastAPI, api_exceptions: dict[type[Exception], int]) -> None:
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
add_exception_handlers(app, APP_ERRORS)
app.include_router(api_router, prefix="/api")
app.include_router(exams_router, prefix="/api")


@app.get("/health", tags=["health"])
async def health() -> dict:
    return {"status": "ok"}

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)