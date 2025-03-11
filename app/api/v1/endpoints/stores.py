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
    account: AccountModel = Depends(AccountModel.get_current_user),
    session: Any = Depends(get_async_session),
    token: str = Depends(oauth2_scheme),
) -> StoreOutput:
    try:
        print(f'STORE RAW DATA::: {store}')
        store_data = json.loads(store)
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Invalid store data format",
                "message": f"JSON parsing error: {str(e)}"
            }
        )

    try:
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