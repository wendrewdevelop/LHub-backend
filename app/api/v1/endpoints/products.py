import json
from uuid import UUID
from typing import Optional, Any
from fastapi import (
    APIRouter, 
    status, 
    Depends, 
    UploadFile, 
    File, 
    Form,
    Body,
    HTTPException
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_async_session
from app.models import (
    StoreModel,
    AccountModel,
    ProductModel
)
from app.schemas import ProductOutput, ProductInput
from app.core import oauth2_scheme


router = APIRouter(
    prefix="/products",
    tags=["products"],
    responses={
        404: {
            "description": "Not found"
        }
    },
)

# 2. Atualize a rota para converter o Pydantic model para dict
@router.post("/", response_model=ProductOutput)
async def new_product(
    product_input: ProductInput = Body(...),
    account: AccountModel = Depends(AccountModel.get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> ProductOutput:
    try:
        product_data = product_input.model_dump()
        product_data["account_id"] = str(account.get("id"))  # Converte UUID para string, se necessário
        product_item = await ProductModel.add(
            session=session,
            data=product_data
        )
        return ProductOutput.model_validate(product_item)
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=str(e)
        )
    
@router.get("/")
async def get(
    account_id: UUID,
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_async_session)
):
    try:
        products = await ProductModel.get_store_products(
            account_id=account_id, 
            session=session
        )
        return products
    except Exception as error:
        raise {
            "message": f'{error}'
        }