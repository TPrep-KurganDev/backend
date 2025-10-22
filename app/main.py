from fastapi import FastAPI
from app.api.routes.auth import router as api_router
from app.api.routes.exams import router as exams_router
from infrastructure.models import Base
from infrastructure.database import engine, SessionLocal
from mocks.mock_users import create_mock_users

app = FastAPI(
title="Backend API",
version="0.1.0",
docs_url="/api/docs",
openapi_url="/api/openapi.json",
)

#Проверить запуск uvicorn app.main:app --reload

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

    # Замоканые пользователи
    # Не забывать чистить бд. Можно запустить helpers/clear_db.py

    db = SessionLocal()
    create_mock_users(db)
    db.close()

@app.get("/health", tags=["health"])
async def health() -> dict:
    return {"status": "ok"}


app.include_router(api_router, prefix="/api")
app.include_router(exams_router, prefix="/api")