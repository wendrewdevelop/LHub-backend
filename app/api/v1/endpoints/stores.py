import json
from typing import Optional, Any
from fastapi import APIRouter, status, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_async_session
from app.models import StoreModel, AccountModel
from app.schemas import StoreOutput, StoreInput


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
    account: AccountModel = Depends(AccountModel.get_current_user),
    session: Any = Depends(get_async_session)
) -> StoreOutput:
    print(f'Account::: {account}')
    store_data = json.loads(store)
    print(f'STORE::: {store_data}')
    store_obj = StoreInput(
        **store_data
    )
    store_item = await StoreModel.add(
        store=store_obj,
        session=session
    )
    
    return StoreOutput.model_validate(store_item)