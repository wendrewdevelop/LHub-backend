import json
from typing import Optional
from fastapi import APIRouter, status, Depends, UploadFile, File, Form
from app.models.account import AccountModel
from app.schemas.account import AccountInput


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
async def post(account: str = Form(...), file: Optional[UploadFile] = File(None)):
    print(f'ACCOUNT STRING::: {account}')
    # Converta o JSON string para dicionário
    account_data = json.loads(account)
    account_obj = AccountInput(**account_data)

    return await AccountModel.add(account_obj, file)


@router.put("/", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(AccountModel.get_current_user)])
async def put(account: AccountInput):
    ...


@router.get("/", dependencies=[Depends(AccountModel.get_current_user)])
async def get(account_id: str = None):
    return AccountModel.get(account_id)