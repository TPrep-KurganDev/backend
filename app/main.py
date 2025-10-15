from fastapi import FastAPI
from app.api.routes.users import router as api_router
from infrastructure.models import Base
from infrastructure.database import engine


app = FastAPI(
title="Backend API",
version="0.1.0",
docs_url="/api/docs",
openapi_url="/api/openapi.json",
)

#Проверить запуск uvicorn app.main:app --reload
#Пока что для запуска, делаем DATABASE_URL = sqlite:///./test.db

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

@app.get("/health", tags=["health"])
async def health() -> dict:
    return {"status": "ok"}


app.include_router(api_router, prefix="/api")