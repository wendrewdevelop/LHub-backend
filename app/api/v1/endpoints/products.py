import json
from typing import Optional, Any
from fastapi import (
    APIRouter, 
    status, 
    Depends, 
    UploadFile, 
    File, 
    Form
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


router = APIRouter(
    prefix="/products",
    tags=["products"],
    responses={
        404: {
            "description": "Not found"
        }
    },
)

@classmethod
async def add(
    cls,
    session: AsyncSession,
    data: dict,  # Alterado para receber dicionário
):
    try:
        new_product = cls(**data)
        session.add(new_product)
        await session.commit()
        await session.refresh(new_product)
        return new_product
    except Exception as error:
        await session.rollback()  # Importante para transações assíncronas
        raise ValueError(f"Database error: {str(error)}") from error

# 2. Atualize a rota para converter o Pydantic model para dict
@router.post("/", response_model=ProductOutput)
async def new_product(
    product: str = Form(...),
    account: AccountModel = Depends(AccountModel.get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> ProductOutput:
    try:
        product_data = json.loads(product)
        product_data["account_id"] = str(account.get("id"))  # Converta UUID para string
        
        # Valide e converta para dict
        product_input = ProductInput(**product_data)
        product_dict = product_input.model_dump()
        
        # Adicione ao banco
        product_item = await ProductModel.add(
            session=session,
            data=product_dict
        )
        
        # Converta o modelo ORM para Pydantic
        return ProductOutput.model_validate(product_item)
    
    except Exception as e:
        raise e