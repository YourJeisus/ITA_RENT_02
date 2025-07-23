"""Remove string length limits for listings fields

Revision ID: 825f9faa3abf
Revises: a96fa69894d3
Create Date: 2025-07-24 00:31:40.563526

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '825f9faa3abf'
down_revision: Union[str, None] = 'a96fa69894d3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
