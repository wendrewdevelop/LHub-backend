import uuid
import traceback
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
from sqlalchemy.dialects.postgresql import (
    UUID, 
    TIMESTAMP,
    JSONB
)
from sqlalchemy.orm import relationship
from enum import Enum
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.core import Base


class OrderStatusEnum(str, Enum):
    RECEBIDO = "RECEBIDO"
    EM_PREPARO = "EM_PREPARO"
    ENVIADO = "ENVIADO"
    ENTREGUE = "ENTREGUE"
    CANCELADO = "CANCELADO"
    

class OrderModel(Base):
    __tablename__ = "tb_order"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    total_amount = Column(Float, nullable=False)
    shipping_address = Column(JSON, nullable=False)
    payment_info = Column(JSON, nullable=False)
    status = Column(
        SQLEnum(OrderStatusEnum), 
        default=OrderStatusEnum.RECEBIDO
    )
    status_history = Column(
        JSONB,
        default=[],
        nullable=False
    )
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now()                  
    )
    store_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("tb_store.id"), 
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=True      
    )

    items = relationship(
        "OrderItemModel", 
        back_populates="order",
        lazy="selectin"
    )
    store = relationship(
        "StoreModel", 
        back_populates="orders"
    ) 

    @classmethod
    async def get_store_orders(
        cls, 
        session: AsyncSession, 
        store_id: UUID
    ):
        try:
            query = await session.execute(
                select(
                    cls.id,
                    cls.total_amount,
                    cls.shipping_address,
                    cls.payment_info,
                    cls.status,
                    cls.status_history,
                    cls.created_at,
                    cls.store_id
                ).where(
                    cls.store_id == store_id
                )
            )
            result = query.mappings().all()
            return result
        except Exception as error:
            print(error)
            traceback.print_exc()

    @classmethod
    async def get_new_orders(
        cls, 
        session: AsyncSession, 
        store_id: UUID
    ):
        try:
            query = await session.execute(
                select(
                    cls.id,
                    cls.total_amount,
                    cls.shipping_address,
                    cls.payment_info,
                    cls.status,
                    cls.status_history,
                    cls.created_at,
                    cls.store_id
                ).where(
                    cls.store_id == store_id,
                    cls.status == "RECEBIDO"
                )
            )
            result = query.mappings().all()
            return result
        except Exception as error:
            print(error)
            traceback.print_exc()


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