import os
import math
import pytz
import pandas as pd
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import update

# Import your local Session and Product model
from .database import SessionLocal  # Adjust the import path if needed
from .models import Product         # Adjust the import path if needed

def chunker(seq, size):
    """
    Generator that yields subsequences of length `size` from the list `seq`.
    """
    for pos in range(0, len(seq), size):
        yield seq[pos : pos + size]

def batch_update_deleted_at(drop_ids_file_path: str, batch_size: int = 100):
    """
    Reads a file of IDs (one per line or in CSV) into a list,
    then updates `deletedAt` in batches for all matching products.
    """
    # 1) Load drop_ids from a text/CSV file using Pandas
    #    - If it's truly just one ID per line in a plain text file,
    #      you can use `names=["id"]` and `header=None`.
    # df = pd.read_csv(drop_ids_file_path, names=["id"], header=None)
    
    # Convert to a Python list of IDs
    # id_list = df["id"].tolist()
    with open(drop_ids_file_path, "r") as f:
        id_list = [line.strip() for line in f.readlines()]
    
    # 2) Open a DB session
    with SessionLocal() as session:
        
        total_ids = len(id_list)
        print(f"Total IDs to update: {total_ids}")
        
        # 3) Chunk through the ID list
        processed = 0
        for chunk in chunker(id_list, batch_size):
            # 4) Perform a bulk UPDATE for this chunk
            #    Using the Query API in SQLAlchemy:
            #    Filter by id in the chunk and set deletedAt = now()
            session.query(Product)\
                   .filter(Product.id.in_(chunk))\
                   .update({Product.deletedAt: datetime.now(pytz.UTC)},
                           synchronize_session=False)
            
            session.commit()  # Commit each batch

            processed += len(chunk)
            print(f"Processed {processed} of {total_ids} IDs...")

    print("Done updating deletedAt for drop_ids.")

if __name__ == "__main__":
    # Example usage
    drop_ids_file = "app/drop_ids.txt"
    batch_update_deleted_at(drop_ids_file, batch_size=100)
