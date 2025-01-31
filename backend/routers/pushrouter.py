from fastapi import APIRouter, Depends, File, UploadFile, Form
from database.models import PushList

from database.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from tools import (
    TokenData,
    get_arq_connection,
    get_current_user,
    save_files_to_tmp,
    parse_socks5_uri
)
from typing import List, Annotated

from arq import ArqRedis
import uuid
from datetime import datetime
from datetime import timezone as datetime_timezone
from tzlocal import get_localzone
import pytz

from arq.jobs import Job
from config import LIMIT_SPEED
import dateutil.parser




router = APIRouter()

# Постановка задачи в очередь Arq и ожидание результата
async def enqueue_push_message_job(
    arq: ArqRedis,
    job_name: str,
    user_id: int,
    type_db: str,
    type_message: str,
    text_message: str,
    files_list: List[str],
    limit: int,
    hours_limit: float = 0,
    hours_limit_msg: float = 0,
    limit_speed: str = 'max',
    job_id: str = '',
    push_date = None,
    timezone = None,
    *args
):
    if job_id == '':
        job_id = f'telethon_job:{str(uuid.uuid4())}'

    if push_date is None:
        job = await arq.enqueue_job(
            job_name, 
            user_id, 
            type_db, 
            type_message, 
            text_message, 
            files_list, 
            limit, 
            hours_limit, 
            limit_speed,
            int(hours_limit_msg),
            timezone,
            _job_id=job_id, 
            *args
        )
    else:
        t = pytz.timezone(timezone)
        target_date = push_date.astimezone(t)

        job = await arq.enqueue_job(
            job_name, 
            user_id,
            type_db,
            type_message, 
            text_message, 
            files_list, 
            limit,
            hours_limit,
            limit_speed,
            int(hours_limit_msg),
            timezone,
            _job_id=job_id,
            _defer_until=target_date,
            *args
        )

    return {'status': 'ok', 'detail': ''}



@router.get('/get_all')
async def get_all_push(
    user_id: int | None = None,
    status: str | None = None,
    user: TokenData = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    is_completed = False

    if user_id is None:
        return {'status': 'fail', 'detail': 'not found user_id'}
    if status is None:
        return {'status': 'fail', 'detail': 'not found status'}
    if status in ['wait','finished']:
        if status == 'finished':
            is_completed = True

    else:
        return {'status': 'fail', 'detail': 'status is not valid'}
    
    query = await session.execute(select(PushList).where(PushList.telethon_id == user_id, PushList.is_completed == is_completed))
    res = query.scalars().all()
    
    return_data = []

    if res is not None:
        for i in res:
            return_data.append(
                {
                    'id': i.id,
                    'name': i.name,
                    'job_id': i.job_id,
                    'type': i.type,
                    'media_list': i.media_list,
                    'date_push': i.date_push,
                    'timezone': i.timezone
                }
            )        

    return return_data


@router.post("/check_push_message")
async def check_push_message(
    type_message: Annotated[str, Form()],
    text_message: Annotated[str, Form()],

    user_id: int | str | None = None,
    files_list: List[UploadFile] = File(...),
    current_user: TokenData = Depends(get_current_user),
    arq: ArqRedis = Depends(get_arq_connection),
):
    if user_id is None:
        return {'status': 'fail', 'detail': 'not found user_id'}
    
    if not isinstance(user_id, int):
        if not user_id.isdigit():
            return {'status': 'fail', 'detail': 'not found user_id'} 
    
    user_id = int(user_id)

    if type_message == 'text':
        result = await enqueue_push_message_job(arq, 'send_push_message', user_id, type_message, text_message, [])
        
    else:
        saved_file_paths = await save_files_to_tmp(files_list)
        result = await enqueue_push_message_job(arq, 'send_push_message', user_id, type_message, text_message, saved_file_paths)

    return result


@router.delete('/delete_push')
async def delete_push(
    push_id: int | None = None,
    current_user: TokenData = Depends(get_current_user),
    arq: ArqRedis = Depends(get_arq_connection),
    session: AsyncSession = Depends(get_session)
):
    query = await session.execute(select(PushList).where(PushList.id == push_id))
    res = query.scalar_one_or_none()

    if res is None:
        return {'status': 'fail', 'detail': 'not found push'}
    
    try:
        job = Job(job_id=res.job_id, redis=arq)
        await job.abort()
    except Exception as ex:
        # return {'status': 'fail', 'detail': 'failed to abort job'}
        print(ex)
    finally:
        # await session.delete(res)
        res.is_completed = True
        await session.commit()

    return {'status': 'ok', 'detail': ''}



@router.post("/send_push_messages")
async def send_push_message(
    type_db: Annotated[str, Form()],
    limit: Annotated[str, Form()],
    type_message: Annotated[str, Form()],
    text_message: Annotated[str, Form()],
    push_name: Annotated[str, Form()],
    date_push: Annotated[str, Form()],
    date_push_not_utc: Annotated[str, Form()],
    timezone: Annotated[str, Form()],
    hours_limit: Annotated[str, Form()],
    hours_limit_msg: Annotated[str, Form()],
    limit_speed: Annotated[str, Form()],
    is_use_proxy: Annotated[bool, Form()],
    proxy_data: Annotated[str, Form()],

    files_list: List[UploadFile] = File(...),

    user_id: int | None = None,
    current_user: TokenData = Depends(get_current_user),
    arq: ArqRedis = Depends(get_arq_connection),
    session: AsyncSession = Depends(get_session)
):
    if user_id is None:
        return {'status': 'fail', 'detail': 'not found user_id'}
    
    if limit_speed != 'max':
        if LIMIT_SPEED.get(limit_speed) is None:
            return {'status': 'fail', 'detail': 'not found limit_speed'}

    try:
        hours_limit = float(hours_limit)
    except Exception as ex:
        return {'status': 'fail', 'detail': 'hours limit not valid'}
    
    try:
        date_push = dateutil.parser.parse(date_push)
        date_push_not_utc = dateutil.parser.parse(date_push_not_utc)
        if int(limit) < 0:
            return {'status': 'fail', 'detail': 'limit less than zero'}
        
    except Exception as ex:
        print(ex)
        return {'status': 'fail', 'detail': str(ex)}
    
    job_id = f'telethon_job:{str(uuid.uuid4())}'

    if type_message == 'text':
        result = await enqueue_push_message_job(
            arq, 
            'send_push_db_message',
            user_id,
            type_db, 
            type_message, 
            text_message, 
            [], 
            int(limit), 
            limit_speed=limit_speed,
            hours_limit_msg=hours_limit_msg,
            hours_limit=hours_limit,
            timezone=timezone, 
            push_date=date_push, 
            job_id=job_id
        )
    else:
        saved_file_paths = await save_files_to_tmp(files_list)
        result = await enqueue_push_message_job(
            arq, 
            'send_push_db_message',
            user_id, 
            type_db, 
            type_message, 
            text_message, 
            saved_file_paths, 
            int(limit),
            limit_speed=limit_speed,
            hours_limit_msg=hours_limit_msg,
            hours_limit=hours_limit, 
            timezone=timezone, 
            push_date=date_push, 
            job_id=job_id
        )

    
    push_data = PushList(
        name=push_name,
        job_id=job_id,
        type=type_message,
        text_push=text_message,
        date_push=date_push_not_utc,
        timezone=timezone,

        type_db=type_db,
        limit=limit,
        telethon_id=user_id
    )
    
    session.add(push_data)
    await session.commit()

    result = {'status': 'ok', 'detail': {
        'job_id': job_id
    }}
    return result



# formData.append('is_use_proxy', isUseProxy.value);
#   formData.append('proxy_data', selectedProxy.value);

@router.post("/send_push_messages_now")
async def send_push_message(
    type_db: Annotated[str, Form()],
    limit: Annotated[str, Form()],
    type_message: Annotated[str, Form()],
    text_message: Annotated[str, Form()],
    push_name: Annotated[str, Form()],
    hours_limit: Annotated[str, Form()],
    hours_limit_msg: Annotated[str, Form()],
    timezone: Annotated[str, Form()],
    limit_speed: Annotated[str, Form()],
    is_use_proxy: Annotated[bool, Form()],
    proxy_data: Annotated[str, Form()],
    

    files_list: List[UploadFile] = File(...),
    user_id: int | None = None,
    current_user: TokenData = Depends(get_current_user),
    arq: ArqRedis = Depends(get_arq_connection),
    session: AsyncSession = Depends(get_session)
):
    if user_id is None:
        return {'status': 'fail', 'detail': 'not found user_id'}
    
    if limit_speed != 'max':
        if LIMIT_SPEED.get(limit_speed) is None:
            return {'status': 'fail', 'detail': 'not found limit_speed'}


    try:
        hours_limit = float(hours_limit)
    except Exception as ex:
        return {'status': 'fail', 'detail': 'hours limit not valid'}
    
    try:
        if int(limit) < 0:
            return {'status': 'fail', 'detail': 'limit less than zero'}
        
    except Exception as ex:
        return {'status': 'fail', 'detail': str(ex)}
    

    if is_use_proxy:
        job = await arq.enqueue_job('set_proxy', type_db, proxy_data)
        await job.result()
    else:
        job = await arq.enqueue_job('set_proxy', type_db, None)
        await job.result()
    
    job_id = f'telethon_job:{str(uuid.uuid4())}'

    if type_message == 'text':
        result = await enqueue_push_message_job(
            arq, 
            'send_push_db_message', 
            user_id, 
            type_db, 
            type_message, 
            text_message, 
            [], 
            int(limit), 
            hours_limit,
            hours_limit_msg,
            limit_speed,
            timezone=timezone,
            job_id=job_id
        )
    else:
        saved_file_paths = await save_files_to_tmp(files_list)
        print(saved_file_paths)
        result = await enqueue_push_message_job(
            arq, 
            'send_push_db_message', 
            user_id, 
            type_db, 
            type_message, 
            text_message, 
            saved_file_paths, 
            int(limit),
            hours_limit,
            hours_limit_msg,
            limit_speed,
            timezone=timezone,
            job_id=job_id
        )

    
    push_data = PushList(
        name=push_name,
        job_id=job_id,
        type=type_message,
        text_push=text_message,
        date_push=datetime.now(tz=datetime_timezone.utc),
        timezone='Europe/Moscow',
        type_db=type_db,
        limit=limit,
        telethon_id=user_id
    )
    
    session.add(push_data)
    await session.commit()

    result = {'status': 'ok', 'detail': {
        'job_id': job_id
    }}
    return result
