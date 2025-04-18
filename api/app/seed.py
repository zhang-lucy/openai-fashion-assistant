import json
import uuid
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import Product
from .clip_embedder import embed_text
from dotenv import load_dotenv

from transformers import AutoTokenizer, AutoModel
import torch
load_dotenv()

def load_products(db: Session):
    # Delete all existing products
    db.query(Product).delete()
    db.commit()
    print("Cleared existing products from database")

    with open("app/meta_Amazon_Fashion_100.json", "r") as f:
        data = json.load(f)["data"]

    for i in range(len(data)):
        if i % 10 == 0:
            print(f"inserted {i} products")
        item = data[i]

        image_urls = [
            img.get("hi_res") or img.get("large")
            for img in item["images"]
            if img.get("hi_res") or img.get("large")
        ]
        product = Product(
            id=str(uuid.uuid4()),
            title=item["title"],
            imageUrls=image_urls,
            features=item.get("features", []),
            description="\n".join(item.get("description", [])),
            average_rating=item.get("average_rating"),
            rating_number=item.get("rating_number"),
            store=item.get("main_category"),
        )
        db.add(product)
    db.commit()
    print(f"Inserted {len(data)} products.")


def main():
    db = SessionLocal()
    try:
        load_products(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
