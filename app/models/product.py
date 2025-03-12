import traceback
import uuid
from typing import Optional
from sqlalchemy import (
    Column, 
    Integer, 
    String, 
    ForeignKey,
    DECIMAL,
    Boolean
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core import Base
from app.schemas import ProductInput


class ProductModel(Base):
    __tablename__ = "tb_product"

    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    price = Column(
        DECIMAL(
            precision=10, 
            scale=2
        ), 
        nullable=False
    )
    in_stock = Column(
        Boolean,
        default=True
    )
    qtd_in_stock = Column(
        Integer,
        default=1
    )
    # Pronta entrega?
    ready_delivery = Column(
        Boolean,
        default=False
    )
    account_id = Column(
        UUID(as_uuid=True),
        ForeignKey('tb_account.id'),
        nullable=False
    )

    account = relationship(
        "AccountModel", 
        back_populates="product"
    )
    order_items = relationship(
        "OrderItemModel", 
        back_populates="product"
    )

    @classmethod
    async def add(
        cls,
        session: AsyncSession,
        data,
    ):
        try:
            new_product = cls(**data)
            session.add(new_product)
            await session.commit()
            await session.refresh(new_product)

            return new_product

        except Exception as error:
            print(error)
            traceback.print_exc()

    @classmethod
    async def get_store_products(
        cls,
        session: AsyncSession,
        account_id
    ):
        try:
            query = await session.execute(
                select(
                    cls.id,
                    cls.name,
                    cls.description,
                    cls.price,
                    cls.in_stock,
                    cls.qtd_in_stock,
                    cls.ready_delivery,
                ).where(
                    cls.account_id == account_id
                )
            )
            result = query.mappings().all()
            return result
        except Exception as error:
            print(error)
            traceback.print_exc()