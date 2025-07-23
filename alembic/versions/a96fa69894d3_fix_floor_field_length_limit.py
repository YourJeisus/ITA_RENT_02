"""Fix floor field length limit

Revision ID: a96fa69894d3
Revises: d8063bfa6e97
Create Date: 2025-07-24 00:14:03.923264

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a96fa69894d3'
down_revision: Union[str, None] = 'd8063bfa6e97'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Увеличиваем размер поля floor с 20 до 100 символов
    op.alter_column('listings', 'floor', 
                   existing_type=sa.String(20),
                   type_=sa.String(100),
                   existing_nullable=True)


def downgrade() -> None:
    # Возвращаем размер поля floor обратно к 20 символам
    op.alter_column('listings', 'floor',
                   existing_type=sa.String(100), 
                   type_=sa.String(20),
                   existing_nullable=True)
