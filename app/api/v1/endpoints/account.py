import json
from typing import Optional
from fastapi import APIRouter, status, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_async_session
from app.models.account import AccountModel
from app.schemas.account import AccountInput, AccountOutput


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
    session: AsyncSession = Depends(get_async_session)
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


@router.put("/", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(AccountModel.get_current_user)])
async def put(account: AccountInput):
    ...


@router.get("/", dependencies=[Depends(AccountModel.get_current_user)])
async def get(account_id: str = None):
    return AccountModel.get(account_id)