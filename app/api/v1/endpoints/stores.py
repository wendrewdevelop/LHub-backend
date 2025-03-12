import json
from typing import Optional, Any
from fastapi import (
    APIRouter, 
    status, 
    Depends, 
    UploadFile, 
    File, 
    Form,
    HTTPException
)
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_async_session
from app.models import StoreModel, AccountModel
from app.schemas import StoreOutput, StoreInput
from app.core import oauth2_scheme


router = APIRouter(
    prefix="/stores",
    tags=["stores"],
    responses={
        404: {
            "description": "Not found"
        }
    },
)

@router.post("/", response_model=StoreOutput)
async def new_store(
    store: str = Form(...),
    account: AccountModel = Depends(AccountModel.get_current_user),  # ← Remove a dependência duplicada do token
    session: AsyncSession = Depends(get_async_session),
) -> StoreOutput:
    try:
        store_data = json.loads(store)
        print(f'Dados da loja recebidos: {store_data}')
        
        store_obj = StoreInput(**store_data)
        store_item = await StoreModel.add(
            store=store_obj, 
            session=session
        )
        return StoreOutput.model_validate(store_item)
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating store: {str(e)}"
        )