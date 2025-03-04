import json
from fastapi import FastAPI, APIRouter
from datetime import datetime, timedelta
from typing import Union, Any
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from typing_extensions import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from decouple import config
from app.schemas import Token, TokenData, AccountInput, AuthAccountToken
from app.models import AccountModel
from app.db import get_async_session
from app.core.security import (
    create_access_token,
    access_token_expires as token_expires,
    password_reset_tokens,
    blacklisted_tokens
)


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={
        404: {
            "description": "Not found"
        }
    },
)

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Any = Depends(get_async_session)
):
    # Autenticação assíncrona com await
    user = await AccountModel.authenticate_user(
        email=form_data.username,
        password=form_data.password,
        session=session
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Configurar tempo de expiração do token
    access_token_expires = timedelta(minutes=30)
    
    # Criar payload do token com dados serializáveis
    access_token = create_access_token(
        data={"sub": user["email"]},  # Usar email ou ID como identificador
        expires_delta=access_token_expires
    )

    # Obter dados do usuário de forma assíncrona
    user_data = await AccountModel.get_user_email(form_data.username, session)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": [
            {
                "email": user_data["email"],
                "id": str(user_data["id"])
            }
        ]
    }


@router.get("/users/me/")
async def read_users_me(current_user: Annotated[AuthAccountToken, Depends(AccountModel.get_current_user)]):
    return current_user


@router.get("/users/me/items/")
async def read_own_items(current_user: Annotated[AccountModel, Depends(AccountModel.get_current_active_user)]):
    return [{"owner": current_user}]


@router.post("/logout")
async def revoke_token(token: str):
    # Add the token to the in-memory blacklist
    blacklisted_tokens.append(token)
    return {"message": "Token revoked"}


@router.get("/users/forgot/password")
async def forgot_password(email: str):
    """The reset password flow start here,
    That endpoint generate a special access token to given
    a next step of flow.

    Args:
        email (str): user email

    Returns:
        _type_: returns a special access token
    """
    user = AccountModel.get_user_email(email)
    access_token_expires = timedelta(minutes=config("ACCESS_TOKEN_EXPIRE_MINUTES"))

    if email in user[0].get("mail"):
        # Gere um token de redefinição de senha e armazene-o
        token = create_access_token(
            data={"sub": user[0].get("mail")},
            expires_delta=access_token_expires
        )
        password_reset_tokens[email] = token
        # Aqui, você normalmente enviaria um e-mail com o token para o usuário
        return password_reset_tokens[email]
    else:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")


@router.post("/users/password/reset", dependencies=[Depends(AccountModel.get_current_user)])
async def reset_password(email: str, new_password: str):
    """Last step of reset password flow is here.
    Now we use token, new password and email gived.

    Args:
        email (str): user email
        new_password (str): new user password
        token (str): token gived
    """

    user = AccountModel.get_user_email(email)
    user_id = user[0].get("user_id")

    if email in user[0].get("mail"):
        # Verifique o token e redefina a senha
        AccountModel.change_password(
            user_id=user_id,
            new_password=new_password
        )
        # Limpe o token de redefinição de senha, uma vez que ele foi usado
        return {"message": "Senha redefinida com sucesso"}
    else:
        raise HTTPException(status_code=404, detail="Token inválido ou expirado")