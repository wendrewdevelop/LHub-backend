"""Corrige coluna cep

Revision ID: 22d773ff724f
Revises: dbd3e1e8ef15
Create Date: 2025-03-06 18:36:18.511432

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '22d773ff724f'
down_revision: Union[str, None] = 'dbd3e1e8ef15'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
