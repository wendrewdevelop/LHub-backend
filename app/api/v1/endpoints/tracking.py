from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_async_session
from app.models import OrderModel, OrderStatusEnum
from app.schemas.tracking import OrderStatusResponse, OrderStatusUpdate
from app.models.account import AccountModel


router = APIRouter(
    tags=["Tracking"]
)

@router.get("/orders/{order_id}/status", response_model=OrderStatusResponse)
async def get_order_status(
    order_id: str,
    current_user: AccountModel = Depends(AccountModel.get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    order = await db.get(OrderModel, order_id)
    
    if not order or order.account_id != current_user.id:
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
        : AccountModel = Depends(AccountModel.get_current_user),  # Implemente esta validação
    db: AsyncSession = Depends(get_async_session)
):
    order = await db.get(OrderModel, order_id)
    
    if not order or order.store_id != current_user.store_id:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    # Atualiza histórico
    order.status_history.append({
        "status": order.status.value,
        "timestamp": timezone.utc(),
        "notes": status_data.notes
    })
    
    order.status = OrderStatusEnum[status_data.status.value]
    order.updated_at = timezone.utc()
    
    await db.commit()
    await db.refresh(order)
    
    return OrderStatusResponse(
        current_status=order.status.value,
        last_update=order.updated_at,
        history=order.status_history
    )