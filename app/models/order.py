import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, 
    ForeignKey, 
    Enum as SQLEnum, 
    JSON, 
    Integer, 
    Float, 
    DateTime,
    func
)
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy.orm import relationship
from enum import Enum
from app.core import Base


class OrderStatusEnum(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class OrderModel(Base):
    __tablename__ = "tb_order"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    total_amount = Column(Float, nullable=False)
    shipping_address = Column(JSON, nullable=False)
    payment_info = Column(JSON, nullable=False)  # {gateway: "stripe", charge_id: "ch_123"}
    status = Column(
        SQLEnum(OrderStatusEnum), 
        default=OrderStatusEnum.PENDING
    )
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),  # Python-side default
        server_default=func.now()                    # Database-side default
    )
    account_id = Column(
        UUID(as_uuid=True),
        ForeignKey('tb_account.id'),
        nullable=False
    )
    store_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("tb_store.id"), 
        nullable=False
    )

    items = relationship(
        "OrderItemModel", 
        back_populates="order",
        lazy="selectin"
    )
    account = relationship(
        "AccountModel",
        back_populates="order"
    )
    store = relationship(
        "StoreModel", 
        back_populates="orders"
    ) 


class OrderItemModel(Base):
    __tablename__ = "tb_order_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("tb_order.id"), 
        nullable=False
    )
    product_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("tb_product.id"), 
        nullable=False
    )
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)

    order = relationship(
        "OrderModel", 
        back_populates="items",
        lazy="joined"
    )
    product = relationship(
        "ProductModel",
        back_populates="order_items"
    )