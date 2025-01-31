from database.database import Base


from sqlalchemy import Integer, Column, String, DateTime, BigInteger, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from datetime import datetime, timezone
from uuid import uuid4



class TelethonUser(Base):
    __tablename__ = 'telethon_accounts'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    api_id = Column(BigInteger, default=0)
    api_hash = Column(String, default=0)
    date_create = Column(DateTime(timezone=True), default=lambda: datetime.now(tz=timezone.utc))

    session_name = Column(String, default=lambda: str(uuid4()) + '.session')

    push_lists = relationship('PushList', back_populates='telethon')
    rd_base_data = relationship('RDusers', back_populates='telethon')
    fd_base_data = relationship('FDusers', back_populates='telethon')



class FDusers(Base):
    __tablename__ = 'fd_users'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(BigInteger)
    access_hash = Column(String)
    username = Column(String)
    date_create = Column(DateTime(timezone=True), default=lambda: datetime.now(tz=timezone.utc))

    telethon_id = Column(Integer, ForeignKey('telethon_accounts.id'))
    telethon = relationship('TelethonUser', back_populates='fd_base_data')


class RDusers(Base):
    __tablename__ = 'rd_users'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(BigInteger)
    access_hash = Column(String)
    username = Column(String)
    date_create = Column(DateTime(timezone=True), default=lambda: datetime.now(tz=timezone.utc))

    telethon_id = Column(Integer, ForeignKey('telethon_accounts.id'))
    telethon = relationship('TelethonUser', back_populates='rd_base_data')


class PushList(Base):
    __tablename__ = 'push_list'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String)
    job_id = Column(String)
    type_db = Column(String)
    limit = Column(Integer)
    type = Column(String)
    text_push = Column(String)
    
    media_list = Column(String)
    date_push = Column(DateTime(timezone=True), nullable=False)
    timezone = Column(String)
    is_completed = Column(Boolean, default=False)
    
    telethon_id = Column(Integer, ForeignKey('telethon_accounts.id'))
    telethon = relationship('TelethonUser', back_populates='push_lists')



class SocksProxy(Base):
    __tablename__ = 'socks_proxies'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    address = Column(String, nullable=False)
    port = Column(Integer, nullable=False)
    username = Column(String, nullable=True)
    password = Column(String, nullable=True)
    active = Column(Boolean, default=True)

