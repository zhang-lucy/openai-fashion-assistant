"""add HNSW index to embedding column

Revision ID: bc5ec16e83f4
Revises: e87b2044ada8
Create Date: 2025-04-13 11:54:56.249338

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "bc5ec16e83f4"
down_revision: Union[str, None] = "e87b2044ada8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        CREATE INDEX products_embedding_hnsw_idx
        ON products
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 1000);
    """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
        DROP INDEX IF EXISTS products_embedding_hnsw_idx;
    """
    )
