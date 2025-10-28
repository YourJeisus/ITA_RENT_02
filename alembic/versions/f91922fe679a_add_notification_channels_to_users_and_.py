"""add_notification_channels_to_users_and_filters

Revision ID: f91922fe679a
Revises: da096da68aef
Create Date: 2025-10-28 20:07:16.584310

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f91922fe679a'
down_revision: Union[str, None] = 'da096da68aef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Добавляем колонки уведомлений в таблицу users
    op.add_column('users', sa.Column('email_notifications_enabled', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('users', sa.Column('telegram_notifications_enabled', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('users', sa.Column('email_verified_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('email_last_sent_at', sa.DateTime(timezone=True), nullable=True))
    
    # Добавляем колонки каналов уведомлений в таблицу filters
    op.add_column('filters', sa.Column('notify_telegram', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('filters', sa.Column('notify_email', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('filters', sa.Column('notify_whatsapp', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    # Удаляем колонки из таблицы filters
    op.drop_column('filters', 'notify_whatsapp')
    op.drop_column('filters', 'notify_email')
    op.drop_column('filters', 'notify_telegram')
    
    # Удаляем колонки из таблицы users
    op.drop_column('users', 'email_last_sent_at')
    op.drop_column('users', 'email_verified_at')
    op.drop_column('users', 'telegram_notifications_enabled')
    op.drop_column('users', 'email_notifications_enabled')
