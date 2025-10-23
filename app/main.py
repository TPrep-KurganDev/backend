from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from app.api.routes.auth import router as api_router
from app.api.routes.exams import router as exams_router
from infrastructure.models import Base
from infrastructure.database import engine, SessionLocal
from mocks.mock_users import create_mock_users
from mocks.request import do_request
from helpers.clear_db import clear_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)

    # Замоканые пользователи
    # Не забывать чистить бд. Можно запустить helpers/clear_db.py
    clear_db()
    db = SessionLocal()
    create_mock_users(db)
    db.close()
    yield

app = FastAPI(
title="Backend API",
version="0.1.0",
docs_url="/api/docs",
openapi_url="/api/openapi.json",
lifespan=lifespan,
)
app.include_router(api_router, prefix="/api")
app.include_router(exams_router, prefix="/api")


@app.get("/health", tags=["health"])
async def health() -> dict:
    return {"status": "ok"}

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)