from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DATABASE_PATH

import os



engine = create_async_engine(DATABASE_PATH, echo=True)
Base = declarative_base()
async_session: AsyncSession = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)



async def get_session():
    async with async_session() as session:
        async with session.begin():
            yield session