from fastapi import FastAPI
from app.api.routes import router as api_router


app = FastAPI(
title="Backend API",
version="0.1.0",
docs_url="/api/docs",
openapi_url="/api/openapi.json",
)


@app.get("/health", tags=["health"])
async def health() -> dict:
    return {"status": "ok"}


app.include_router(api_router, prefix="/api")