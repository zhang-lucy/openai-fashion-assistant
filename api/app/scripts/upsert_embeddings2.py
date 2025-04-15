import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from .database import SessionLocal
from .models import Product
from .clip_embedder import embed_text
from dotenv import load_dotenv

import json

load_dotenv()


def load_embeddings(
    db: Session,
    df: pd.DataFrame,
    start_index: int = 0,
    batch_size: int = 50,
    refresh_embeddings: bool = False,
):
    i = start_index
    while i < len(df):
        batch_df = df.iloc[i : i + batch_size]

        # Flatten all primary_keys in this batch
        all_keys = set()
        for keys in batch_df["pks"]:
            all_keys.update(eval(keys))

        # Query existing products and check embedding status
        existing = (
            db.query(Product.id, Product.embedding)
            .filter(Product.id.in_(all_keys))
            .all()
        )
        id_to_embedding = {row.id: row.embedding for row in existing}

        # Skip rows where none of the IDs exist or already have embeddings
        filtered_rows = []
        filtered_texts = []
        filtered_primary_keys = []

        for row in batch_df.itertuples():
            primary_keys = eval(row.pks)
            # Keep only IDs that exist and (embedding is None or refresh flag is on)
            valid_keys = [
                pk
                for pk in primary_keys
                if pk in id_to_embedding
                and (id_to_embedding[pk] is None or refresh_embeddings)
            ]
            if valid_keys:
                filtered_rows.append(row)
                filtered_texts.append(row.text_for_embedding)
                filtered_primary_keys.append(valid_keys)

        if not filtered_rows:
            print(f"Skipped batch {i}–{i+batch_size-1} (no valid embedding updates)")
            i += batch_size
            continue

        # Embed only necessary texts
        embeddings = embed_text(filtered_texts)

        # Prepare and execute upserts
        for keys, embedding in zip(filtered_primary_keys, embeddings):
            for pk in keys:
                db.execute(
                    Product.__table__.update()
                    .where(Product.id == pk)
                    .values(embedding=embedding)
                )

        db.commit()
        print(f"Committed batch: {i} → {i + len(batch_df) - 1}")
        i += batch_size

    print(f"Finished embedding update for rows {start_index} to {len(df) - 1}.")


def main(start_index: int = 0, refresh_embeddings: bool = False):
    db = SessionLocal()
    try:
        df = pd.read_csv("app/texts_for_embedding.csv")
        load_embeddings(
            db,
            df,
            start_index=start_index,
            refresh_embeddings=refresh_embeddings,
        )
    finally:
        db.close()


if __name__ == "__main__":
    import sys

    start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    refresh = sys.argv[2].lower() == "true" if len(sys.argv) > 2 else False
    main(start_index=start, refresh_embeddings=refresh)
