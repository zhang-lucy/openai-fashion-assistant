from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime


class ProductBase(BaseModel):
    title: str
    imageUrls: List[str]
    description: Optional[str] = None
    details: Optional[str] = None
    average_rating: Optional[float] = None
    rating_number: Optional[int] = None
    store: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class ProductCreate(ProductBase):
    id: str


class Product(ProductBase):
    id: str
    createdAt: Optional[datetime]
    modifiedAt: Optional[datetime]
    deletedAt: Optional[datetime]
    similarity: Optional[float]

    class Config:
        orm_mode = True
