import traceback
import uuid
from typing import Optional
from datetime import datetime, timezone
from fastapi import (
    HTTPException, 
    UploadFile, 
    File, 
    Form, 
    status,
    Depends
)
import sqlalchemy as db
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import update
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from typing_extensions import Annotated
from jose import (
    jwt, 
    JWTError, 
    ExpiredSignatureError
)
from decouple import config
from app.db.session import session, upload_image
from app.core import ( 
    verify_password, 
    blacklisted_tokens,
    oauth2_scheme,
    Base
)
from app.schemas import AccountInput, TokenData


class AccountModel(Base):
    __tablename__ = "tb_account"

    # Definição das colunas
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    profile_picture = db.Column(db.LargeBinary)
    created_at = db.Column(db.Date, default=func.now())
    updated_at = db.Column(db.Date, default=func.now(), onupdate=func.now())

    @staticmethod
    async def add(
        account: AccountInput,
        file: Optional[UploadFile] = File(None)
    ):
        from app.core.security import hash_password

        print(f'ACCOUNT OBJ::: {account}')

        password = hash_password(account.password)
        query = AccountModel(
            email=account.email,
            password=password.hex()
        )

        try:
            # Inserir os dados na tabela `AccountModel`
            session.add(query)
            session.commit()

            # Caso a imagem seja fornecida, chamar o método `upload_image`
            if file:
                file_content = await file.read()
                await upload_image(
                    item_id=str(query.id),
                    model_instance=AccountModel,
                    column="profile_picture",
                    file_content=file_content
                )

            return query

        except Exception as error:
            print(error)
            traceback.print_exc()
            session.rollback()

        finally:
            session.close()

    def get(account_id):
        query = session.query(
            AccountModel.id.label("id"),
            AccountModel.email.label("store_name")
        )
        if account_id:
            query = query.filter(AccountModel.id==account_id)
        query = query.all()
        try:
            results = AccountModel.dict_columns(query)
            return results
        except Exception as error:
            print(error)
            traceback.print_exc()
        finally:
            session.close()

    def update(update_data: dict):
        """Update data using dict

        Usage:
            update_data = {
                "password": hash_password(new_password).decode("utf8"),
                "store_name": "New Store Name",
                "store_description": "Updated description"
            }

            updated_item = update(user_id="some-user-id", update_data=update_data, session=session)

        Args:
            store_id (str): ID to find on database table
            update_data (dict): dict with data to update (column:key)

        Raises:
            HTTPException: If ID gived is not exist on database table, an exception is raised

        Returns:
            _type_: return item updated
        """

        db_item = session.query(AccountModel).filter(
            AccountModel.id == store_id
        ).first()

        print(f'DB ITEM::: {db_item}')

        if db_item is None:
            raise HTTPException(status_code=404, detail="Item not found")

        # Update the fields you need
        for column, value in update_data.items():
            if hasattr(db_item, column):
                setattr(db_item, column, value)

        session.commit()
        session.refresh(db_item)
        session.close()

        return db_item

    def get_password_email(email: str):
        query = session.query(
            AccountModel.password.label("password"),
            AccountModel.email.label("mail")
        ).filter(AccountModel.email==email)
        query = query.all()
        try:
            results = [passw for passw in query]
            return results[0]
        except Exception as error:
            print(error)
            traceback.print_exc()
        finally:
            session.close()

    def get_user_email(email: str):
        query = session.query(
            AccountModel.id.label("id"),
            AccountModel.email.label("email"),
        ).filter(AccountModel.email==email)
        query = query.all()
        try:
            results = AccountModel.dict_columns(query)
            print(f'RESULTS::: {results}')
            return results
        except Exception as error:
            print(error)
            traceback.print_exc()
        finally:
            session.close()


    def dict_columns(query) -> dict:
        return [{
            "id": data[0],
            "email": data[1]
        } for data in query]
    
    @staticmethod
    def authenticate_user(email: str, password: str):
        # about.wendrew@gmail.com
        # sunsix123
        user = AccountModel.get_password_email(email)
        if not user:
            return False
        if not verify_password(password, user[0]):
            return False
        return user
    
    @staticmethod
    async def get_current_user(token: str):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Decodifica o token
            payload = jwt.decode(token, config("SECRET_KEY"), algorithms=[config("ALGORITHM")])
            username: str = payload.get("sub")
            exps: int = payload.get("exp")

            if username is None:
                raise credentials_exception

            if token in blacklisted_tokens:
                raise credentials_exception

            # Verifica se o token expirou
            if exps is None or datetime.fromtimestamp(exps, tz=timezone.utc) < datetime.now(timezone.utc):
                print("Token expirado ou inválido")
                raise credentials_exception

            token_data = TokenData(username=username, expires=exps)

        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except JWTError:
            raise credentials_exception

        # Verifica se o usuário existe no banco
        user = AccountModel.get_user_email(email=token_data.username)

        if user is None:
            raise credentials_exception

        return user
    
    @staticmethod
    async def get_current_active_user(current_user: Annotated["AccountModel", Depends(get_current_user)]):
        if not current_user:
            raise HTTPException(status_code=400, detail="Inactive user")
        return current_user