"""initial

Revision ID: 8274da30b38f
Revises: 
Create Date: 2025-09-13 14:43:04.198688

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from app.core.security import get_password_hash


revision: str = '8274da30b38f'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('username', sa.String, nullable=False, unique=True),
        sa.Column('hashed_password', sa.String, nullable=False),
    )

    # Добавляем начальных пользователей
    users_table = sa.table(
        'users',
        sa.column('username', sa.String),
        sa.column('hashed_password', sa.String),
    )

    op.bulk_insert(
        users_table,
        [
            {"username": "admin", "hashed_password": get_password_hash("admin123")},
            {"username": "user1", "hashed_password": get_password_hash("user123")},
        ]
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('users')
