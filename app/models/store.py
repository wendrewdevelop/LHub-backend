import traceback
import uuid
from typing import Optional
from sqlalchemy import (
    Column, 
    Integer, 
    String, 
    ForeignKey, 
    Float
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.core import Base
from app.schemas import StoreInput


class StoreModel(Base):
    __tablename__ = "tb_store"

    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    address = Column(String(200), nullable=False)
    cep = Column(
        String(9), 
        nullable=False,
        server_default='00000000'
    )  
    delivery_fee = Column(
        Float,
        default=0.0
    )
    account_id = Column(
        UUID(as_uuid=True),
        ForeignKey('tb_account.id'),
        nullable=False
    )

    account = relationship(
        "AccountModel", 
        back_populates="store"
    )
    orders = relationship(
        "OrderModel",
        back_populates="store"
    )

    @classmethod
    async def add(
        cls,
        store,
        session: AsyncSession
    ):
        try:
            new_store = cls(
                name=store.name,
                description=store.description,
                address=store.address,
                account_id=store.account_id
            )
            session.add(new_store)
            await session.commit()
            await session.refresh(new_store)

            return new_store

        except Exception as error:
            print(error)
            traceback.print_exc()