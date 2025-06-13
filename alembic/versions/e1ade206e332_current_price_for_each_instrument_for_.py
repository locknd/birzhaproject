# alembic/versions/e1ade206e332_current_price_for_each_instrument_for_market_order.py

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import INTEGER

# revision identifiers, used by Alembic.
revision = 'e1ade206e332'
down_revision = 'd8cdc5de8ae6'  # Замените на предыдущую ревизию
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Upgrade schema."""
    # 1) Добавляем колонку current_price в таблицу instruments с разрешением NULL
    op.add_column(
        'instruments',
        sa.Column(
            'current_price',
            sa.Integer,  # Используем Integer для хранения цены
            nullable=True,  # Разрешаем NULL, пока не обновим все данные
            comment='Текущая цена инструмента для рыночного ордера'
        )
    )

    # 2) Вставляем цены для каждого тикера
    op.execute("""
        UPDATE instruments
        SET current_price = 1000000
        WHERE ticker = 'BTCRUB';  -- Пример для BTC
    """)
    op.execute("""
        UPDATE instruments
        SET current_price = 650000
        WHERE ticker = 'ETHRUB';  -- Пример для Ethereum
    """)
    op.execute("""
        UPDATE instruments
        SET current_price = 8000
        WHERE ticker = 'LTCRUB';  -- Пример для Litecoin
    """)
    op.execute("""
        UPDATE instruments
        SET current_price = 20
        WHERE ticker = 'DOGERUB';  -- Пример для Dogecoin
    """)
    op.execute("""
        UPDATE instruments
        SET current_price = 15000
        WHERE ticker = 'SOLRUB';  -- Пример для Solana
    """)
    op.execute("""
        UPDATE instruments
        SET current_price = 5000
        WHERE ticker = 'ADARUB';  -- Пример для Cardano
    """)
    op.execute("""
        UPDATE instruments
        SET current_price = 1000
        WHERE ticker = 'DOTRUB';  -- Пример для Polkadot
    """)
    op.execute("""
        UPDATE instruments
        SET current_price = 1
        WHERE ticker = 'MEMERUB';  -- Пример для MemeCoin
    """)
    op.execute("""
        UPDATE instruments
        SET current_price = 500
        WHERE ticker = 'BCHRUB';  -- Пример для Bitcoin Cash
    """)
    op.execute("""
        UPDATE instruments
        SET current_price = 250
        WHERE ticker = 'XRPRUB';  -- Пример для Ripple
    """)

    # 3) Теперь можно изменить current_price на NOT NULL
    op.alter_column(
        'instruments',
        'current_price',
        nullable=False  # Сделаем колонку обязательной
    )

    # 4) Изменяем типы данных для соответствующих полей в таблицах
    op.alter_column('orders', 'price', type_=sa.Integer, existing_type=sa.Numeric(20, 8), nullable=True)
    op.alter_column('orders', 'quantity', type_=sa.Integer, existing_type=sa.Numeric(20, 8), nullable=False)

    op.alter_column('balances', 'amount', type_=sa.Integer, existing_type=sa.Numeric(20, 8), nullable=False)

    op.alter_column('transactions', 'price', type_=sa.Integer, existing_type=sa.Numeric(20, 8), nullable=False)
    op.alter_column('transactions', 'quantity', type_=sa.Integer, existing_type=sa.Numeric(20, 8), nullable=False)

def downgrade() -> None:
    """Downgrade schema."""
    # 1) Убираем вставку значений для current_price и удаляем колонку
    op.drop_column('instruments', 'current_price')

    # 2) Возвращаем типы данных для price, quantity, amount обратно в Numeric
    op.alter_column('orders', 'price', type_=sa.Numeric(20, 8), existing_type=sa.Integer, nullable=True)
    op.alter_column('orders', 'quantity', type_=sa.Numeric(20, 8), existing_type=sa.Integer, nullable=False)

    op.alter_column('balances', 'amount', type_=sa.Numeric(20, 8), existing_type=sa.Integer, nullable=False)

    op.alter_column('transactions', 'price', type_=sa.Numeric(20, 8), existing_type=sa.Integer, nullable=False)
    op.alter_column('transactions', 'quantity', type_=sa.Numeric(20, 8), existing_type=sa.Integer, nullable=False)
