from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.utils import InsufficientStockError
from app.schemas import (
    OrderCreate,
    OrderItemCreate,
    OrderResponse
)
from app.models import (
    ProductModel
)


async def reserve_inventory(db: AsyncSession, items: List[OrderItemCreate]):
    reserved = []
    try:
        for item in items:
            product = await db.get(ProductModel, item.product_id)
            
            if not product or product.qtd_in_stock < item.quantity:
                raise InsufficientStockError(product_id=item.product_id)
            
            product.qtd_in_stock -= item.quantity
            reserved.append((item.product_id, item.quantity))
        
        await db.commit()
        return reserved
    except:
        await db.rollback()
        raise


async def release_inventory(db: AsyncSession, items: List[tuple]):
    try:
        for product_id, quantity in items:
            product = await db.get(ProductModel, product_id)
            product.qtd_in_stock += quantity
        
        await db.commit()
    except:
        await db.rollback()
        raise