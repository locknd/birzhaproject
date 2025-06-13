"""rub instruments

Revision ID: d8cdc5de8ae6
Revises: 20cddb8d570e
Create Date: 2025-06-12 18:29:16.538245

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import table, column, String, text

# revision identifiers, used by Alembic.
revision: str = 'd8cdc5de8ae6'
down_revision: Union[str, None] = '20cddb8d570e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Add currency column with default RUB ---
    op.add_column(
        'instruments',
        sa.Column(
            'currency',
            sa.String(length=3),
            nullable=False,
            server_default='RUB',
            comment='Валюта расчёта (RUB по умолчанию)',
        ),
    )
    op.create_index(
        'ix_instruments_currency',
        'instruments',
        ['currency'],
        unique=False,
    )

    # --- Ensure status defaults to ACTIVE for new rows ---
    op.alter_column(
        'instruments',
        'status',
        existing_type=sa.Enum(name='instrumentstatusenum'),
        nullable=False,
        server_default=text("'ACTIVE'::instrumentstatusenum"),
    )

    # --- Seed ruble instruments ---
    instr_table = table(
        'instruments',
        column('ticker',   String),
        column('name',     String),
        column('currency', String),
    )
    op.bulk_insert(
        instr_table,
        [
            {'ticker': 'BTCRUB',  'name': 'Bitcoin / RUB',      'currency': 'RUB'},
            {'ticker': 'ETHRUB',  'name': 'Ethereum / RUB',     'currency': 'RUB'},
            {'ticker': 'LTCRUB',  'name': 'Litecoin / RUB',     'currency': 'RUB'},
            {'ticker': 'XRPRUB',  'name': 'Ripple / RUB',       'currency': 'RUB'},
            {'ticker': 'BCHRUB',  'name': 'Bitcoin Cash / RUB', 'currency': 'RUB'},
            {'ticker': 'DOGERUB', 'name': 'Dogecoin / RUB',     'currency': 'RUB'},
            {'ticker': 'SOLRUB',  'name': 'Solana / RUB',       'currency': 'RUB'},
            {'ticker': 'ADARUB',  'name': 'Cardano / RUB',      'currency': 'RUB'},
            {'ticker': 'DOTRUB',  'name': 'Polkadot / RUB',     'currency': 'RUB'},
            {'ticker': 'MEMERUB', 'name': 'MemeCoin / RUB',     'currency': 'RUB'},
        ],
    )


def downgrade() -> None:
    # --- Remove seeded ruble instruments ---
    op.execute(
        "DELETE FROM instruments WHERE ticker IN ("
        "'BTCRUB','ETHRUB','LTCRUB','XRPRUB','BCHRUB',"
        "'DOGERUB','SOLRUB','ADARUB','DOTRUB','MEMERUB')"
    )

    # --- Revert status default ---
    op.alter_column(
        'instruments',
        'status',
        existing_type=sa.Enum(name='instrumentstatusenum'),
        nullable=False,
        server_default=None,
    )

    # --- Drop currency column and index ---
    op.drop_index('ix_instruments_currency', table_name='instruments')
    op.drop_column('instruments', 'currency')