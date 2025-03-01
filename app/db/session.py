import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
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

        args = {
            'connect_args': {
                'options': f'-c timezone=America/Sao_Paulo'
            }
        }

        self.connection = f"postgresql://{user}:{password}@{host}/{database}"
        self.engine = create_engine(self.connection, **args)

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
            self.Session = scoped_session(sessionmaker(bind=self.engine))
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
    user=config("NAME"),
    password=config("PASSWORD"),
    host=config("HOST"),
    port=5432,
    database=config("DATABASE")
)
session = postgresql.create_session()