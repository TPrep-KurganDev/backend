from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from typing import List


router = APIRouter()


class Item(BaseModel):
    id: int
    name: str
    price: float


FAKE_DB = [
    Item(id=1, name="Laptop", price=1299.99),
    Item(id=2, name="Phone", price=799.00),
    Item(id=3, name="Mouse", price=35.50),
]


@router.get("/", tags=["root"])
async def root() -> dict:
    return {"message": "Hello from backend 🚀"}


@router.get("/items", response_model=List[Item], tags=["items"])
async def list_items(limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0)) -> List[Item]:
    return FAKE_DB[offset: offset + limit]


@router.get("/items/{item_id}", response_model=Item, tags=["items"])
async def get_item(item_id: int) -> Item:
    for it in FAKE_DB:
        if it.id == item_id:
            return it
    raise HTTPException(status_code=404, detail="Item not found")