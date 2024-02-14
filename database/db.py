import os

from sqlalchemy import Column, Integer

from sqlalchemy.orm import declarative_base, sessionmaker, declared_attr
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from dotenv import load_dotenv


load_dotenv()


class PreBase:

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)


Base = declarative_base(cls=PreBase)
engine = create_async_engine(os.getenv('DB_URL'))
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession)
session = AsyncSessionLocal()
