import os
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import async_session
from database import models
from sqlalchemy import select, delete
import telethon
from typing import Union
from uuid import uuid4

from redis import Redis
from tools import get_formatted_date_filename, parse_socks5_uri
from datetime import datetime
from config import REDIS_PUBSUB_CHANNEL

import logging
from database.tasks_models import TelegramTasks


from telethon.types import InputPeerUser
import asyncio


logger = logging.getLogger('tasks')


# Добавление новой сессии в базу данных
async def add_new_session(api_id: int, api_hash: str, session_name: str):
    
    
    session: AsyncSession

    try:
        
        async with async_session() as session:
            async with session.begin():
                new_session = models.TelethonUser(
                    api_id=api_id,
                    api_hash=api_hash,
                    session_name=session_name,
                )
                session.add(new_session)
                await session.commit()

                return {'status': 'ok', 'session_id': new_session.id}
    except Exception as ex:
        logger.error(f'Failed to write the data to table - {str(ex)}')




async def delete_session(db_id):
    
    session: AsyncSession
    async with async_session() as session:
        async with session.begin():

            await session.execute(delete(models.TelethonUser).where(models.TelethonUser.id == db_id))
            await session.commit()


# Выход из аккаунта
async def exit_from_account(ctx, user_id: int):
    try:
        await delete_session(user_id)

        
        telethon_worker: TelegramTasks = ctx['telethon_worker']
        await telethon_worker.exit_from_account(user_id)

        # if data:

        return True
    except Exception as ex:
        logger.error(f'Error in exit from acc {user_id} - {str(ex)}')

        return False


async def set_proxy(ctx,  account_db_id: int, proxy_data: str):
    telethon_worker: TelegramTasks = ctx['telethon_worker']
    redis: Redis = ctx['redis_client']

    data = None
    if proxy_data != "null":
        data = parse_socks5_uri(proxy_data)
    await telethon_worker.set_proxy_client(account_db_id, data, redis)

    return True


# Получаем инфу об аккаунте
async def get_account_info(ctx, account_db_id: int):
    telethon_worker: TelegramTasks = ctx['telethon_worker']
    redis: Redis = ctx['redis_client']

    logger.info(f'Get account info - {account_db_id}')

    data = await telethon_worker.get_account_info(account_db_id, redis)

    if data is not None:
        return data
    
    return {'status': 'fail', 'detail': 'need create session'}


async def send_phone_request(ctx, db_id: int, phone: str):
    telethon_worker: TelegramTasks = ctx['telethon_worker']
    logger.info(f'Get account info - {db_id}')

    try:
        await telethon_worker.send_phone(db_id, phone)

        return {'status': 'fail', 'detail': 'need code'}
    except Exception as ex:
        logger.error(f'Failed to input phone - {str(ex)}')
        return {'status': 'fail', 'detail': 'failed to input phone', 'full_detail': str(ex)}


# Подготовка сессии для создания
async def create_telethon_session(ctx, api_id: str, api_hash):
    telethon_worker: TelegramTasks = ctx['telethon_worker']

    session_name = str(uuid4()) + '.session'

    try:
        logger.info('Create telethon session')
        res = await telethon_worker.append_account(
            api_id=api_id,
            api_hash=api_hash,
            session_name=session_name
        )

        return {'status': 'fail', 'detail': 'input phone', 'tmp_key': res.get('key')}
    except Exception as ex:
        logger.error(f"Failed to create session - {str(ex)}")
        return {'status': 'fail', 'detail': 'failed to create session'}


# Вход в тг аккаунт
async def sign_in(ctx, db_id: str = '', code: Union[str, None] = '', password: Union[str, None] = ''):
    telethon_worker: TelegramTasks = ctx['telethon_worker']
    tg_data = await telethon_worker.telegram_data(db_id)
    redis: Redis = ctx['redis_client']

    try:
        await telethon_worker.sign_in(db_id, code, password)

        is_user_auth = await telethon_worker.check_user_auth(db_id)
        if is_user_auth:
            user_data = await telethon_worker.get_account_info(db_id, redis)

            data = await add_new_session(
                tg_data.api_id,
                tg_data.api_hash,
                tg_data.session_name
            )

            await telethon_worker.change_key(db_id, data.get('session_id'))


            return user_data
        else:
            if code:
                return {'status': 'fail', 'detail': 'need password'}
            else:
                return {'status': 'ok', 'detail': 'need code'}

    except telethon.errors.PhoneCodeInvalidError:
        return {'status': 'fail', 'detail': 'failed to input code'}

    except telethon.errors.SessionPasswordNeededError:
        if code:
            tg_data.code = code 
        return {'status': 'fail', 'detail': 'need password'}

    # Общая обработка ошибок
    except Exception as ex:
        if 'The password' in str(ex):
            return {'status': 'fail', 'detail': 'failed to input password'}
        
        return {'status': 'fail', 'detail': 'failed to sign in', 'full_detail': str(ex)}
    


# Отправлять пуш уведомления самому себе
async def send_push_message(ctx, db_id, type_message: str = 'text', text_message: str = '', files: list[str] = []):
    telethon_worker: TelegramTasks = ctx['telethon_worker']

    res = await telethon_worker.check_message(
        db_id=db_id,
        type_message=type_message,
        text_message=text_message,
        files=files
    )

    return res


# Отправлять пуш уведомления самому себе
async def send_push_db_message(ctx, db_id: int, type_db: str = 'fd', type_message: str = 'text', text_message: str = '', files: list[str] = [], limit: int = 10000, hours_limit: int = 0, limit_speed:str = 'max',  hours_limit_msg: float = 0, timezone: str = 'Europe/Moscow'):
    telethon_worker: TelegramTasks = ctx['telethon_worker']
    redis: Redis = ctx['redis_client']

    # async def send_pushes_task():
    res = await telethon_worker.send_pushes(
        db_id,
        redis,
        type_db,
        type_message,
        text_message,
        files,
        limit,
        hours_limit,
        limit_speed,
        hours_limit_msg,
        timezone,
        ctx['job_id']
    )
    
    # asyncio.ensure_future(send_pushes_task())

    return res



