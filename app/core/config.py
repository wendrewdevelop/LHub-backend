from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from sqlalchemy.ext.declarative import declarative_base
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic_settings import BaseSettings
from decouple import config


app = FastAPI()
Base = declarative_base()

class Settings(BaseSettings):
    CORREIOS_API_KEY: str = config("CORREIOS_API_KEY")
    # ... outras configs
    
    class Config:
        env_file = ".env"


async def startup():
    FastAPICache.init(InMemoryBackend(), prefix="lh-cache")


app.add_event_handler("startup", startup)