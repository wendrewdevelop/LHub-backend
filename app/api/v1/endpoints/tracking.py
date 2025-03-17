from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
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
    session: AsyncSession = Depends(get_async_session)
):
    order = await OrderModel.tracking_order(
        session=session,
        checkout_id=order_id
    )
    print(f'ORDER::: {order[0]}')
    
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    # Converter o endereço para string formatada
    address = order[0].shipping_address
    print(address)
    formatted_address = (
        f'{address.get("street")}, {address.get("number")} - {address.get("neighborhood")}, '
        f'{address.get("city")}/{address.get("state")}'
    )

    # Converter o histórico de status
    status_history = []
    for entry in order[0].status_history:
        print(f'ENTRY::: {entry}')
        status_history.append({
            "status": entry.get("status"),
            "timestamp": entry.get("timestamp")
        })

    return {
        "current_status": order[0].status.value,
        "last_update": order[0].updated_at.isoformat(),
        "history": status_history,
        "total_amount": order[0].total_amount,
        "delivery_estimate": order[0].created_at.replace(hour=order[0].created_at.hour + 1).isoformat(),
        "shipping_address": formatted_address
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