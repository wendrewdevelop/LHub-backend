from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy.ext.declarative import declarative_base
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from app.db.models.room import Room
from app.db.models.character import Character


app = FastAPI()
Base = declarative_base()