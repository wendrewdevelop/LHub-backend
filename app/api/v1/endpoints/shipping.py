from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from fastapi_cache.decorator import cache
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_async_session
from app.schemas import (
    ShippingCalculateRequest, 
    ShippingOptionResponse,
    LocalDeliveryRequest,
    LocalDeliveryResponse
    
)
from app.models import AccountModel, StoreModel
from app.services import ShippingCalculator, LocalDeliveryCalculator


router = APIRouter(
    tags=["shipping"]
)

@router.post("/shipping/calculate", response_model=List[ShippingOptionResponse])
@cache(expire=60 * 30)  # Cache de 30 minutos
async def calculate_shipping(
    request: ShippingCalculateRequest,
    calculator: ShippingCalculator = Depends(),
    session: AsyncSession = Depends(get_async_session)
):
    try:
        return await calculator.calculate(request, session)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao calcular fretes: {str(e)}"
        )
    
    
@router.post("/shipping/local", response_model=LocalDeliveryResponse)
async def calculate_local_delivery(
    request: LocalDeliveryRequest,
    session: Any = Depends(get_async_session)
):
    store = await session.get(
        StoreModel, 
        request.store_id
    )
    if not store:
        raise HTTPException(404, "Loja não encontrada")
    
    return await LocalDeliveryCalculator().calculate(
        store, 
        request.destination_cep
    )