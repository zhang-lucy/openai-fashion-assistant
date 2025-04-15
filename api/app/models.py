from sqlalchemy import Column, Integer, Float, String, DateTime, Text, ARRAY
from sqlalchemy.sql import func
from .database import Base
from pgvector.sqlalchemy import Vector


class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    imageUrls = Column(ARRAY(String), nullable=False)
    description = Column(Text)
    details = Column(Text)
    features = Column(ARRAY(String), default=[])
    average_rating = Column(Float)
    rating_number = Column(Integer)
    store = Column(String)
    embedding = Column(Vector(512), nullable=True)
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    modifiedAt = Column(DateTime(timezone=True), onupdate=func.now())
    deletedAt = Column(DateTime(timezone=True), nullable=True)
