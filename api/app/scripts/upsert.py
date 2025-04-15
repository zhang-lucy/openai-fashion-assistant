import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from .database import SessionLocal
from .models import Product
from .clip_embedder import embed_text
from dotenv import load_dotenv

from transformers import AutoTokenizer, AutoModel
import torch

load_dotenv()


def load_products(
    db: Session,
    df: pd.DataFrame,
    start_index: int = 0,
    batch_size: int = 50,
):
    batch_count = 0

    for i in range(start_index, len(df)):
        item = df.iloc[i]
        if i % 1000 == 0:
            print(f"Processed {i} products")

        title = item["title"]
        description = ",".join(item.get("description", []))

        image_urls = [item["image_url"]]
        features = None
        description = item.get("description")

        average_rating = item.get("average_rating")
        rating_number = item.get("rating_number")
        if rating_number:
            rating_number = int(rating_number)
        store = item.get("store")

        stmt = (
            insert(Product)
            .values(
                id=item["primary_key"],
                title=title,
                imageUrls=image_urls,
                features=features,
                description=description,
                average_rating=average_rating,
                rating_number=rating_number,
                store=store,
            )
            .on_conflict_do_update(
                index_elements=["id"],
                set_={
                    "title": title,
                    "imageUrls": image_urls,
                    "features": features,
                    "description": description,
                    "average_rating": average_rating,
                    "rating_number": rating_number,
                    "store": store,
                },
            )
        )

        db.execute(stmt)
        batch_count += 1

        if batch_count >= batch_size:
            db.commit()
            batch_count = 0
            print(f"Committed batch ending at row {i}")

    if batch_count > 0:
        db.commit()
        print(f"Final commit for remaining {batch_count} products.")

    print(f"Finished upserting {len(df) - start_index} products.")


def main(start_index: int = 0):
    db = SessionLocal()
    try:
        df = pd.read_csv("app/meta_Amazon_Fashion.csv")
        load_products(
            db,
            df,
            start_index=start_index,
        )
    finally:
        db.close()


if __name__ == "__main__":
    import sys

    start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    update = sys.argv[2].lower() == "true" if len(sys.argv) > 2 else True
    main(start_index=start)
