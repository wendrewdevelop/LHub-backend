from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_async_session
from app.models import OrderModel, OrderStatusEnum
from app.schemas.tracking import OrderStatusResponse, OrderStatusUpdate
from app.models.account import AccountModel


router = APIRouter(
    tags=["tracking"]
)

@router.get("/orders/{order_id}/status", response_model=OrderStatusResponse)
async def get_order_status(
    order_id: str,
    current_user: AccountModel = Depends(AccountModel.get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    order = await db.get(OrderModel, order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    return {
        "current_status": order.status.value,
        "last_update": order.updated_at,
        "history": order.status_history
    }


@router.put("/orders/{order_id}/status", response_model=OrderStatusResponse)
async def update_order_status(
    order_id: str,
    status_data: OrderStatusUpdate,
    current_user: AccountModel = Depends(AccountModel.get_current_user), 
    db: AsyncSession = Depends(get_async_session)
):
    order = await db.get(OrderModel, order_id)
    print(f'ORDER ID::: {order_id}')
    print(f'STATUS DATA::: {status_data}')
    
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    if not order.status_history:
        order.status_history = []

    new_entry = {
        "status": order.status.value,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "notes": status_data.notes
    }
    order.status_history = [
        *order.status_history, 
        new_entry
    ]
    order.status = OrderStatusEnum(status_data.status)
    order.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(order)
    
    return {
        "current_status": order.status.value,
        "last_update": order.updated_at,
        "status_history": order.status_history
    }