import uuid
from sqlalchemy import (
    Column, 
    ForeignKey, 
    Integer, 
    Float,
    DateTime,
    select
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import func
from sqlalchemy.orm import relationship, selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.core import Base
from app.schemas import CartItemCreate


class CartModel(Base):
    __tablename__ = "tb_carts"
    
    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    user_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("tb_account.id"), 
        unique=True
    )
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    
    items = relationship(
        "CartItemModel", 
        back_populates="cart", 
        cascade="all, delete-orphan"
    )

    @property
    def total(self):
        return sum(item.total_price for item in self.items)


class CartItemModel(Base):
    __tablename__ = "tb_cart_items"
    
    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    cart_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("tb_carts.id")
    )
    product_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("tb_product.id")
    )
    quantity = Column(Integer, default=1)
    
    cart = relationship(
        "CartModel", 
        back_populates="items"
    )
    product = relationship("ProductModel")

    @property
    def unit_price(self):
        return self.product.price if self.product else 0.0
    
    @property
    def total_price(self):
        return self.unit_price * self.quantity


async def get_user_cart(db: AsyncSession, user_id: str):
    result = await db.execute(
        select(CartModel)
        .where(CartModel.user_id == user_id)
        .options(
            selectinload(CartModel.items)
            .selectinload(CartItemModel.product)
        )
    )
    return result.scalar_one_or_none()


async def add_to_cart(session: AsyncSession, user_id: str, item: CartItemCreate):
    cart = await get_user_cart(session, user_id)
    
    if not cart:
        cart = CartModel(user_id=user_id)
        session.add(cart)
        await session.commit()
        await session.refresh(cart)
    
    # Verifica se o item já existe
    existing_item = next(
        (i for i in cart.items if str(i.product_id) == item.product_id),
        None
    )
    
    if existing_item:
        existing_item.quantity += item.quantity
    else:
        new_item = CartItemModel(
            cart_id=cart.id,
            product_id=item.product_id,
            quantity=item.quantity
        )
        session.add(new_item)
    
    await session.commit()
    
    return cart