"""add_floor_normalization_fields

Revision ID: ca610d1ada57
Revises: 02c2447c7fa9
Create Date: 2025-11-05 15:55:31.022494

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ca610d1ada57'
down_revision: Union[str, None] = '02c2447c7fa9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Добавляем нормализованные поля для этажей
    op.add_column('listings', sa.Column('floor_number', sa.Integer(), nullable=True))
    op.add_column('listings', sa.Column('is_first_floor', sa.Boolean(), nullable=True))
    op.add_column('listings', sa.Column('is_top_floor', sa.Boolean(), nullable=True))
    
    # Создаем индексы для оптимизации фильтрации
    op.create_index('idx_listing_floor_number', 'listings', ['floor_number'], unique=False)
    op.create_index('idx_listing_floor_flags', 'listings', ['is_first_floor', 'is_top_floor'], unique=False)


def downgrade() -> None:
    # Удаляем индексы
    op.drop_index('idx_listing_floor_flags', table_name='listings')
    op.drop_index('idx_listing_floor_number', table_name='listings')
    
    # Удаляем столбцы
    op.drop_column('listings', 'is_top_floor')
    op.drop_column('listings', 'is_first_floor')
    op.drop_column('listings', 'floor_number')
