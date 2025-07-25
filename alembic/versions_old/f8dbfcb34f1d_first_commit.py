"""First Commit

Revision ID: f8dbfcb34f1d
Revises: 
Create Date: 2025-05-13 00:03:49.583355

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f8dbfcb34f1d'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('instruments',
    sa.Column('ticker', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('status', sa.Enum('ACTIVE', 'DELISTED', name='instrumentstatusenum'), nullable=False),
    sa.PrimaryKeyConstraint('ticker')
    )
    op.create_index(op.f('ix_instruments_ticker'), 'instruments', ['ticker'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(), nullable=False),
    sa.Column('password_hash', sa.String(), nullable=False),
    sa.Column('api_key', sa.String(), nullable=False),
    sa.Column('role', sa.Enum('USER', 'ADMIN', name='roleenum'), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_api_key'), 'users', ['api_key'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_table('balances',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('ticker', sa.String(), nullable=False),
    sa.Column('amount', sa.Numeric(precision=20, scale=8), nullable=False),
    sa.ForeignKeyConstraint(['ticker'], ['instruments.ticker'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_balances_id'), 'balances', ['id'], unique=False)
    op.create_table('orders',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('ticker', sa.String(), nullable=False),
    sa.Column('side', sa.Enum('BUY', 'SELL', name='ordersideenum'), nullable=False),
    sa.Column('qty', sa.Numeric(precision=20, scale=8), nullable=False),
    sa.Column('price', sa.Numeric(precision=20, scale=8), nullable=True),
    sa.Column('status', sa.Enum('NEW', 'PARTIALLY_EXECUTED', 'EXECUTED', 'CANCELLED', name='orderstatusenum'), nullable=False),
    sa.Column('filled_qty', sa.Numeric(precision=20, scale=8), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['ticker'], ['instruments.ticker'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_orders_id'), 'orders', ['id'], unique=False)
    op.create_table('transactions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('buy_order_id', sa.Integer(), nullable=False),
    sa.Column('sell_order_id', sa.Integer(), nullable=False),
    sa.Column('ticker', sa.String(), nullable=False),
    sa.Column('qty', sa.Numeric(precision=20, scale=8), nullable=False),
    sa.Column('price', sa.Numeric(precision=20, scale=8), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['buy_order_id'], ['orders.id'], ),
    sa.ForeignKeyConstraint(['sell_order_id'], ['orders.id'], ),
    sa.ForeignKeyConstraint(['ticker'], ['instruments.ticker'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_transactions_id'), 'transactions', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_transactions_id'), table_name='transactions')
    op.drop_table('transactions')
    op.drop_index(op.f('ix_orders_id'), table_name='orders')
    op.drop_table('orders')
    op.drop_index(op.f('ix_balances_id'), table_name='balances')
    op.drop_table('balances')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_api_key'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_instruments_ticker'), table_name='instruments')
    op.drop_table('instruments')
    # ### end Alembic commands ###
