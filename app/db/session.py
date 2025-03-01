import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from fastapi import HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from decouple import config


class PostgreSql:
    """
        Classe que agrupa as funções de
        gerenciamento do PostgreSql.
    """

    def __init__(self, user, password, host, port, database):
        """
            Classe que instancia as conexões com
            o serviço PostgreSql.
            PARAMETROS:
                user: Username do PostgreSql;
                password: Senha do PostgreSql;
                host: Ponto de acesso do PostgreSql;
                port: Porta do ponto de acesso do PostgreSql;
                database: Banco de dados do PostgreSql.
        """

        connection = config("DATABASE_URL_DEV") \
                        if config("ENV") == "DEV" else config("DATABASE_URL_PROD")
        self.connection = connection
        self.engine = create_async_engine(self.connection)

    def get_engine(self):
        """
            Obtém a sessão com o PostgreSql
            RETURN:
                Retorna a engine
        """

        return self.engine

    def create_session(self):
        """
            Cria uma sessão com o PostgreSql.
            RETURN:
                Retorna a sessão criada.
        """

        try:
            self.Session = scoped_session(sessionmaker(
                bind=self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            ))
            self.session = self.Session()
            return self.session
        except Exception as error:
            print(f"ERROR: funcion {PostgreSql.create_session.__name__} -> error -> {str(error)}")
            return str(error)

    def close_engine(self):
        """
            Obtém a sessão com o PostgreSql
            RETURN:
                Fecha a engine
        """

        try:
            self.engine.dispose()
        except Exception as error:
            print(f"ERROR: funcion {PostgreSql.close_engine.__name__} -> error -> {str(error)}")


async def upload_image(
        item_id: str,
        model_instance: object,
        column: str,
        file: UploadFile = File(...)
    ):
        # Buscar o registro específico pelo `item_id`
        query = session.query(model_instance).filter(model_instance.id == item_id).first()

        if not query:
            raise HTTPException(status_code=404, detail="Data not found")

        # Ler o conteúdo do arquivo enviado
        image_data = await file.read()

        # Usar `setattr` para atualizar a coluna dinamicamente
        setattr(query, column, image_data)

        # Commit no banco de dados
        session.commit()
        session.refresh(query)

        return JSONResponse(content={"message": "Image uploaded successfully"})


postgresql = PostgreSql(
    user=config("NAME_DEV") if config("ENV") == "DEV" else config("NAME_PROD"),
    password=config("PASSWORD_DEV") if config("ENV") == "DEV" else config("PASSWORD_PROD"),
    host=config("HOST_DEV") if config("ENV") == "DEV" else config("HOST_PROD"),
    port=5432,
    database=config("DATABASE")
)
session = postgresql.create_session()