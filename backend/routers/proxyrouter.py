from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from typing import List

from database.database import get_session  # Убедитесь, что вы импортируете ваш get_session
from database.models import SocksProxy



import aiohttp
from aiohttp_socks import ProxyType, ProxyConnector, ChainProxyConnector


router = APIRouter()


@router.get("/")
async def get_proxies(
    limit: int = 10,
    skip: int = 0,
    session: AsyncSession = Depends(get_session)
):
    query = select(SocksProxy).offset(skip).limit(limit)
    result = await session.execute(query)
    proxies = result.scalars().all()
    return proxies


@router.post("/")
async def add_proxy(
    address: str,
    port: str,
    username: str = None,
    password: str = None,
    session: AsyncSession = Depends(get_session)
):
    port = int(port)
    proxy = SocksProxy(address=address, port=port, username=username, password=password)
    session.add(proxy)
    await session.commit()
    # await session.refresh(proxy)
    return proxy


@router.put("/{proxy_id}")
async def edit_proxy(
    proxy_id: int,
    address: str,
    port: int,
    username: str = None,
    password: str = None,
    session: AsyncSession = Depends(get_session)
):
    query = select(SocksProxy).filter(SocksProxy.id == proxy_id)
    result = await session.execute(query)
    proxy = result.scalar_one_or_none()

    if not proxy:
        raise HTTPException(status_code=404, detail="Proxy not found")

    proxy.address = address
    proxy.port = port
    proxy.username = username
    proxy.password = password

    session.add(proxy)
    await session.commit()
    # await session.refresh(proxy)
    return proxy


@router.delete("/{proxy_id}")
async def delete_proxy(
    proxy_id: int,
    session: AsyncSession = Depends(get_session)
):
    query = select(SocksProxy).filter(SocksProxy.id == proxy_id)
    result = await session.execute(query)
    proxy = result.scalar_one_or_none()

    if not proxy:
        raise HTTPException(status_code=404, detail="Proxy not found")

    await session.delete(proxy)
    await session.commit()
    return {"message": "Proxy deleted successfully"}


@router.post("/{proxy_id}/check")
async def check_proxy(
    proxy_id: int,
    session: AsyncSession = Depends(get_session)
):
    query = select(SocksProxy).filter(SocksProxy.id == proxy_id)
    result = await session.execute(query)
    proxy = result.scalar_one_or_none()

    if not proxy:
        raise HTTPException(status_code=404, detail="Proxy not found")

    # Логика проверки прокси
    try:
        # Здесь вы можете добавить проверку соединения с прокси
        # Например, использовать библиотеку socks или requests
        # is_valid = True  # Пример результата проверки
        is_valid = False
        
        connector = ProxyConnector(
            proxy_type=ProxyType.SOCKS5,
            host=proxy.address,
            port=proxy.port,
            username=proxy.username,
            password=proxy.password,
            rdns=True
        )
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get('https://web.telegram.org/k/') as response:
                is_valid = True
        return {"id": proxy_id, "status": "valid" if is_valid else "invalid"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
