from fastapi import APIRouter, Depends, HTTPException, Query

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from typing import List, Optional

from database.models import FDusers, RDusers
from database.database import get_session
from tools import get_current_user, TokenData



router = APIRouter()

@router.get("/fdusers")
async def get_fdusers(
    current_user: TokenData = Depends(get_current_user),
    limit: int = 10,
    skip: int = 0,
    session: AsyncSession = Depends(get_session)
):
    query = select(FDusers).offset(skip).limit(limit)
    result = await session.execute(query)
    users = result.scalars().all()

    total_query = select(func.count(FDusers.id))
    total_result = await session.execute(total_query)
    total = total_result.scalar()

    return {
        "total": total,       
        "users": users,
        "limit": limit,       
        "skip": skip
    }


@router.get("/rdusers")
async def get_rdusers(
    current_user: TokenData = Depends(get_current_user),
    limit: int = 10,
    skip: int = 0,
    session: AsyncSession = Depends(get_session)
):
    query = select(RDusers).offset(skip).limit(limit)
    result = await session.execute(query)
    users = result.scalars().all()

    total_query = select(func.count(RDusers.id))
    total_result = await session.execute(total_query)
    total = total_result.scalar()

    return {
        "total": total,
        "users": users,
        "limit": limit,
        "skip": skip
    }


@router.get("/fdusers/search")
async def search_fdusers(
    current_user: TokenData = Depends(get_current_user), 
    user_id: Optional[int] = Query(None),
    username: Optional[str] = Query(None),
    limit: int = 10,
    skip: int = 0,
    session: AsyncSession = Depends(get_session)
):
    query = select(FDusers)


    if user_id is not None:
        query = query.where(FDusers.user_id == user_id)
    if username is not None:
        query = query.where(FDusers.username == username)
    
    query = query.offset(skip).limit(limit)
    result = await session.execute(query)
    users = result.scalars().all()

    total_query = select(func.count(FDusers.id))
    if user_id is not None:
        total_query = total_query.where(FDusers.user_id == user_id)
    if username is not None:
        total_query = total_query.where(FDusers.username == username)
    
    total_result = await session.execute(total_query)
    total = total_result.scalar()

    if not users:
        raise HTTPException(status_code=404, detail="No FDusers found with given criteria")

    return {
        "total": total,
        "users": users,
        "limit": limit,
        "skip": skip
    }


@router.get("/rdusers/search")
async def search_rdusers(
    current_user: TokenData = Depends(get_current_user), 
    user_id: Optional[int] = Query(None),
    username: Optional[str] = Query(None),
    limit: int = 10,
    skip: int = 0,
    session: AsyncSession = Depends(get_session)
):
    query = select(RDusers)

    if user_id is not None:
        query = query.where(RDusers.user_id == user_id)
    if username is not None:
        query = query.where(RDusers.username == username)


    query = query.offset(skip).limit(limit)
    result = await session.execute(query)
    users = result.scalars().all()

    total_query = select(func.count(RDusers.id))
    if user_id is not None:
        total_query = total_query.where(RDusers.user_id == user_id)
    if username is not None:
        total_query = total_query.where(RDusers.username == username)

    total_result = await session.execute(total_query)
    total = total_result.scalar()

    if not users:
        raise HTTPException(status_code=404, detail="No RDusers found with given criteria")

    return {
        "total": total,
        "users": users,
        "limit": limit,
        "skip": skip
    }
