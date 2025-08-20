"""Added role enum to user

Revision ID: 821b6e917022
Revises: fc5123dd0f2b
Create Date: 2025-08-20 19:22:06.742750

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '821b6e917022'
down_revision: Union[str, Sequence[str], None] = 'fc5123dd0f2b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
