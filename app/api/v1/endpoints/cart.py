import uuid
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import (
    AccountModel, 
    get_user_cart, 
    add_to_cart,
    CartItemModel,
    CartModel
)
from app.db import get_async_session
from app.schemas import CartResponse, CartItemCreate


router = APIRouter(
    tags=["cart"]
)

@router.get("/cart", response_model=CartResponse)
async def get_cart(
    current_user: AccountModel = Depends(AccountModel.get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    cart = await get_user_cart(session, current_user.get("id"))
    if not cart:
        return {
            "id": str(uuid.uuid4()), 
            "items": [], 
            "total": 0.0
        }
    # await session.refresh(cart, ["items", "items.product"])   
    return cart


@router.post("/cart/items", response_model=CartResponse)
async def add_item_to_cart(
    item: CartItemCreate,
    current_user: AccountModel = Depends(AccountModel.get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    cart = await add_to_cart(session, current_user.get("id"), item) 
    return CartResponse.model_validate(cart)


@router.put("/cart/items/{item_id}")
async def update_cart_item(
    item_id: UUID,
    quantity: int,
    current_user: AccountModel = Depends(AccountModel.get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    if quantity < 0:
        raise HTTPException(400, "Quantidade não pode ser negativa")
    
    result = await session.execute(
        select(CartItemModel)
        .join(CartModel)
        .where(
            CartItemModel.id == item_id,
            CartModel.user_id == current_user.get("id")
        )
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(404, "Item não encontrado")
    
    item.quantity = quantity
    await session.commit()
    return {"message": "Quantidade atualizada"}


@router.delete("/cart/items/{item_id}")
async def remove_cart_item(
    item_id: UUID,
    current_user: AccountModel = Depends(AccountModel.get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(
        select(CartItemModel)
        .join(CartModel)
        .where(
            CartItemModel.id == item_id,
            CartModel.user_id == current_user.get("id")
        )
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(404, "Item não encontrado")
    
    await session.delete(item)
    await session.commit()
    return {"message": "Item removido"}