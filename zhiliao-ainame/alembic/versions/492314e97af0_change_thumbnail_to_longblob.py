"""change thumbnail to longblob

Revision ID: 492314e97af0
Revises: 5193adb4fd9c
Create Date: 2026-01-15 14:56:26.145571

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import LONGBLOB


# revision identifiers, used by Alembic.
revision: str = '492314e97af0'
down_revision: Union[str, Sequence[str], None] = '5193adb4fd9c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 将 thumbnail 字段从 BLOB 改为 LONGBLOB
    op.alter_column('art', 'thumbnail',
                    existing_type=sa.LargeBinary(),
                    type_=LONGBLOB(),
                    existing_nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    # 将 thumbnail 字段从 LONGBLOB 改回 BLOB
    op.alter_column('art', 'thumbnail',
                    existing_type=LONGBLOB(),
                    type_=sa.LargeBinary(),
                    existing_nullable=False)
