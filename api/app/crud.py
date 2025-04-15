from sqlalchemy.orm import Session
from . import models, schemas


def search_products(db: Session, query: str):
    return (
        db.query(models.Product).filter(models.Product.title.ilike(f"%{query}%")).all()
    )
