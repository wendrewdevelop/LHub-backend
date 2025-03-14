from fastapi import (
    APIRouter, 
    Depends, 
    HTTPException, 
    status,
    Query
)
from typing_extensions import Annotated
from uuid import UUID
from app.services import (
    reserve_inventory, 
    release_inventory, 
    process_payment
)
from app.utils import (
    InsufficientStockError, 
    PaymentProcessingError
)
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import (
    OrderCreate,
    OrderItemCreate,
    OrderResponse
)
from app.db import get_async_session
from app.models import (
    AccountModel,
    OrderModel,
    OrderItemModel,
    OrderStatusEnum,
    StoreModel
)


router = APIRouter(
    prefix="/orders",
    tags=["orders"],
    responses={
        404: {
            "description": "Not found"
        }
    },
)

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    store_id: UUID = Query(...),
    session: AsyncSession = Depends(get_async_session)
):
    print(f'ORDER DATA::: {order_data}')
    try:
        reserved_items = await reserve_inventory(
            session, 
            order_data.items
        )
        print(f'RESERVED ITEMS::: {reserved_items}')
        print(f'ORDER DATA ITEMS::: {order_data.items}')
        payment_result = await process_payment(
            amount=sum(item.unit_price * item.quantity for item in order_data.items),
            payment_method=order_data.payment_method
        )
        print(f'PAYMENT RESULT::: {payment_result}')
        new_order = OrderModel(
            store_id=store_id,
            total_amount=payment_result['amount'],
            shipping_address=order_data.shipping_address,
            payment_info=payment_result,
            status=OrderStatusEnum.RECEBIDO
        )
        
        session.add(new_order)
        await session.flush()  # Persiste temporariamente para obter o ID

        # 4. Adicionar itens ao pedido
        order_items = [
            OrderItemModel(
                order_id=new_order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price
            ) for item in order_data.items
        ]

        session.add_all(order_items)
        await session.commit()  # Confirma todas as operações

        result = await session.execute(
            select(OrderModel)
            .where(OrderModel.id == new_order.id)
            .options(selectinload(OrderModel.items))  # Carregamento eager
        )
        order = result.scalar_one()

        return OrderResponse.model_validate({
            **order.__dict__,
            "items": [
                {
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price
                }
                for item in order.items
            ]
        })

    except InsufficientStockError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estoque insuficiente para o produto {e.product_id}"
        )
    except PaymentProcessingError as e:
        await session.rollback()
        await release_inventory(session, reserved_items)
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=str(e)
        )
    except Exception as e:
        await session.rollback()
        await release_inventory(session, reserved_items)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar pedido: {str(e)}"
        )
    

@router.get("/")
async def get(
    session: AsyncSession = Depends(get_async_session),
    store_id: UUID = None
):
    try:
        orders = await OrderModel.get_store_orders(
            session=session,
            store_id=store_id
        )
        return orders
    except Exception as error:
        raise {
            "message": f'{error}'
        }
    

@router.get("/retrieve/new")
async def get_new_orders(
    session: AsyncSession = Depends(get_async_session),
    store_id: UUID = None
):
    try:
        orders = await OrderModel.get_new_orders(
            session=session,
            store_id=store_id
        )
        return orders
    except Exception as error:
        raise {
            "message": f'{error}'
        }