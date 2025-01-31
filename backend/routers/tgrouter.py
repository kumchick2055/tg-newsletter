from fastapi import APIRouter, Depends, Form, UploadFile, File
from pydantic import BaseModel
from typing import Annotated, List
from arq import ArqRedis

from tools import (
    TokenData,
    get_current_user,
    get_arq_connection,
)

from database.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import TelethonUser


import os
import uuid
from pathlib import Path



router = APIRouter()



@router.get("/get_tg_acc_info")
async def protected_route(
    user_id: int | None = None,
    current_user: TokenData = Depends(get_current_user),
    arq: ArqRedis = Depends(get_arq_connection)
):

    job = await arq.enqueue_job('get_account_info', int(user_id))
    job_res = await job.result()


    return job_res


@router.get("/get_accounts_list")
async def get_accounts_list(
    current_user: TokenData = Depends(get_current_user),
    arq: ArqRedis = Depends(get_arq_connection),
    session: AsyncSession = Depends(get_session)
):
    query = await session.execute(select(TelethonUser))
    res = query.scalars().all()
    
    return_list = []
    if res is not None:
        for i in res:
            return_list.append({
                'account_id': i.id,
                'time_create': i.date_create.isoformat()
            })

    return return_list


class LoginData(BaseModel):
    api_id: str
    api_hash: str


class PhoneSign(BaseModel):
    phone: str


class SmsCode(BaseModel):
    code: str

class PasswordData(BaseModel):
    password: str



@router.post("/create_tg_session")
async def create_tg_session(
    item: LoginData,
    current_user: TokenData = Depends(get_current_user),
    arq: ArqRedis = Depends(get_arq_connection),
    ):

    job = await arq.enqueue_job('create_telethon_session', item.api_id, item.api_hash)
    res = await job.result()

    return res


@router.post("/send_phone_tg")
async def send_phone_tg(
    item: PhoneSign,
    user_id: str | None = None,
    current_user: TokenData = Depends(get_current_user),
    arq: ArqRedis = Depends(get_arq_connection),
    ):

    job = await arq.enqueue_job('send_phone_request', user_id, item.phone)
    res = await job.result()

    return res


@router.post("/send_smscode_tg")
async def send_phone_tg(
    item: SmsCode,
    user_id: str | None = None,
    current_user: TokenData = Depends(get_current_user),
    arq: ArqRedis = Depends(get_arq_connection),
    ):

    job = await arq.enqueue_job('sign_in', user_id, item.code, '')
    res = await job.result()

    return res


@router.post("/send_password_tg")
async def send_password_tg(
    item: PasswordData,
    user_id: str | None = None,
    current_user: TokenData = Depends(get_current_user),
    arq: ArqRedis = Depends(get_arq_connection),
    ):

    job = await arq.enqueue_job('sign_in', user_id, '', item.password)
    res = await job.result()

    return res



@router.delete("/exit_from_account")
async def check_push_message(
    user_id: str | None = None,
    current_user: TokenData = Depends(get_current_user),
    arq: ArqRedis = Depends(get_arq_connection),
):
    job = await arq.enqueue_job('exit_from_account', int(user_id))
    await job.result()

    return {'status': 'ok', 'detail': ''}


