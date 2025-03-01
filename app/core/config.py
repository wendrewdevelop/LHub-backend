from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy.ext.declarative import declarative_base
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient


app = FastAPI()
Base = declarative_base()