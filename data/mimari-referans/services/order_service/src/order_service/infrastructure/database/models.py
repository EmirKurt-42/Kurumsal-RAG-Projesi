"""SQLAlchemy ORM models — the persistence shape of the ``Order`` aggregate.

One aggregate, two tables: the parent row owns its item rows
(``cascade="all, delete-orphan"``), mirroring the domain rule that an
``OrderItem`` cannot exist outside an ``Order``.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Declarative base shared by all ORM models of this service."""


class OrderModel(Base):
    """Row shape of the ``orders`` table."""

    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), index=True)
    status: Mapped[str] = mapped_column(String(20))
    currency: Mapped[str] = mapped_column(String(3))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # selectin: items are eagerly loaded with a second SELECT — the safe
    # strategy under asyncio, where implicit lazy loading would fail.
    items: Mapped[list["OrderItemModel"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class OrderItemModel(Base):
    """Row shape of the ``order_items`` table."""

    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id"))
    product_name: Mapped[str] = mapped_column(String(200))
    # Stored as text: SQLite has no exact decimal type and would silently
    # round through float. With PostgreSQL, switch to Numeric(10, 2).
    unit_price: Mapped[str] = mapped_column(String(20))
    quantity: Mapped[int] = mapped_column(Integer)

    order: Mapped[OrderModel] = relationship(back_populates="items")
