from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from pydantic import BaseModel

from app.database import SessionLocal
from app.models import Product
from app.schemas import Product as ProductSchema
from app.parse_query import parse_query
from app.clip_embedder import embed_text
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.search import SearchService

app = FastAPI()
router = APIRouter()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific origins in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class UserPreferences(BaseModel):
    gender: Optional[str] = None
    price: Optional[str] = None
    styles: Optional[List[str]] = None


@router.post("/products/search", response_model=List[ProductSchema])
def search_products(
    q: str = Query(..., min_length=1),
    preferences: Optional[UserPreferences] = None,
    db: Session = Depends(get_db)
):
    print("Searching for", q)
    print("Preferences", preferences)
    search = SearchService(user_preferences=preferences)
    return search.search_products(q, db)

app.include_router(router)

