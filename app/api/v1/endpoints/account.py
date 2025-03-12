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
    HTTPException
)
from fastapi_cache.decorator import cache
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select
from jose import jwt, JWTError
from decouple import config
from app.db import get_async_session
from app.models.account import AccountModel
from app.models.store import StoreModel
from app.schemas.account import AccountInput, AccountOutput
from app.core import oauth2_scheme


router = APIRouter(
    prefix="/accounts",
    tags=["accounts"],
    responses={
        404: {
            "description": "Not found"
        }
    },
)


@router.post("/")
async def post(
    account: str = Form(...), 
    file: Optional[UploadFile] = File(None),
    session: Any = Depends(get_async_session)
):
    try:
        print(f'ACCOUNT STRING::: {account}')
        account_data = json.loads(account)
        account_obj = AccountInput(**account_data)
        new_account = await AccountModel.add(
            account_obj, 
            session, 
            file
        )

        return AccountOutput(
            email=new_account.email,
            message="Account created!"
        )
    except json.JSONDecodeError:
        raise "Invalid JSON format"
    except Exception as e:
        raise e


@router.put("/")
async def put(account: AccountInput):
    ...


@router.get("/")
async def get(account_id: str = None):
    return AccountModel.get(account_id)


@router.get("/me/store")
async def check_user_has_store(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_async_session)
):
    try:
        payload = jwt.decode(
            token, 
            config("SECRET_KEY"), 
            algorithms=[
                config("ALGORITHM")
            ]
        )
        email = payload.get("sub")
        
        # Query com carregamento do relacionamento store
        result = await session.execute(
            select(AccountModel)
            .options(selectinload(AccountModel.store))  # ← Correção chave
            .where(AccountModel.email == email)
        )
        
        account = result.scalars().first()
        
        return {
            "has_store": bool(account and account.store),
            "store_id": account.store[0].id if account and account.store else None
        }

    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
    

@router.get("/public/store")
async def check_public_store(
    store_id: UUID,
    session: AsyncSession = Depends(get_async_session)
):
    try:
        # Query com carregamento do relacionamento store
        result = await session.execute(
            select(StoreModel)
            .where(StoreModel.id == store_id)
        )
        
        account = result.scalars().first()
        
        return {
            "has_store": bool(account and account.store),
            "store_id": account.store[0].id if account and account.store else None
        }

    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")