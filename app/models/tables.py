from sqlalchemy import Table, Column, String, Float, Integer, Boolean, TIMESTAMP, ForeignKey, func
from .database import metadata

cliente = Table(
    'cliente', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('nome', String(255), nullable=True),
    Column('email', String(255), nullable=True),
    Column('cpf', String(14), nullable=True),
    Column('anonimo', Boolean, default=False),
    Column('created_at', TIMESTAMP, server_default=func.now()),
    Column('updated_at', TIMESTAMP, server_default=func.now(), onupdate=func.now()),
)

pedido = Table(
    'pedido', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('preco_total', Float, nullable=False),
    Column('status', String(50), default="Recebido"),
    Column('cliente_id', Integer, ForeignKey('cliente.id')),
    Column('created_at', TIMESTAMP, server_default=func.now()),
    Column('updated_at', TIMESTAMP, server_default=func.now(), onupdate=func.now()),
)

produto_pedido = Table(
    'produto_pedido', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('produto', String(255), nullable=False),
    Column('preco', Float, nullable=False),
    Column('quantidade', Integer, nullable=False),
    Column('pedido_id', Integer, ForeignKey('pedido.id')),
    Column('created_at', TIMESTAMP, server_default=func.now()),
    Column('updated_at', TIMESTAMP, server_default=func.now(), onupdate=func.now()),
)
