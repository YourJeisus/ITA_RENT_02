"""Remove unique constraint from listings URL field

Revision ID: 3bbdf8a6923d
Revises: 825f9faa3abf
Create Date: 2025-07-29 09:48:30.366297

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3bbdf8a6923d'
down_revision: Union[str, None] = '825f9faa3abf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Удаляем unique constraint с поля url
    try:
        op.drop_constraint('listings_url_key', 'listings', type_='unique')
        print("✅ Удален unique constraint 'listings_url_key' с поля url")
    except Exception as e:
        print(f"⚠️ Ошибка удаления constraint: {e}")
        # Возможно constraint уже отсутствует


def downgrade() -> None:
    # Восстанавливаем unique constraint (если потребуется откат)
    try:
        op.create_unique_constraint('listings_url_key', 'listings', ['url'])
        print("✅ Восстановлен unique constraint 'listings_url_key' на поле url")
    except Exception as e:
        print(f"⚠️ Ошибка восстановления constraint: {e}")
