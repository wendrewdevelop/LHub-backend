# Adicione no início
import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from app.core import Base


# Adicione o caminho do seu projeto
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Modifique esta linha
target_metadata = Base.metadata