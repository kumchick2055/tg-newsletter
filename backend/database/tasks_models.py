import telethon
from dataclasses import dataclass
from typing import Union
import logging
import os
from telethon.types import InputPeerUser, User
from tools import remove_files
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import FDusers, RDusers
from redis.asyncio import Redis

from datetime import datetime, timedelta
from datetime import timezone as datetime_timezone
from tools import get_formatted_date_filename
from config import REDIS_PUBSUB_CHANNEL
from database.database import async_session
from database import models
import asyncio
from random import randint
from config import LIMIT_SPEED
import dateutil.parser

import json

import pytz



logger = logging.getLogger('tasks')


async def add_or_update_user(
        session: AsyncSession,
        model: RDusers | FDusers,
        user,
        db_id,
        hours_limit: int = 0
):
    query = await session.execute(
        select(model).where(
            model.user_id == user.draft.entity.id,
            model.telethon_id == db_id
        )
    )
    res = query.scalar_one_or_none()

    if res is None:
        new_user = model(
            user_id=user.draft.entity.id,
            username=user.draft.entity.username,
            access_hash=user.draft.entity.access_hash,
            telethon_id=db_id
        )
        session.add(new_user)
        await session.commit()
        return True
    else:
        res.username = user.draft.entity.username
        if hours_limit == 0:
            res.date_create = datetime.now(tz=datetime_timezone.utc)
            await session.commit()
            return True
        else:
            time_now = datetime.now(tz=datetime_timezone.utc)
            date_create = res.date_create

            if date_create.tzinfo is None:
                date_create = date_create.replace(tzinfo=datetime_timezone.utc)

            if time_now - date_create <= timedelta(hours=hours_limit):
                return False
            else:
                res.date_create = datetime.now(tz=datetime_timezone.utc)
                await session.commit()
                return True


@dataclass
class TelegramData:
    api_id: int
    api_hash: str
    session_name: str

    # Главный клиент для работы
    client: telethon.TelegramClient

    phone: Union[None | str] = None
    # Хэш мобилки для дальнейшей авторизации
    phone_hash: Union[None | str] = None

    code: Union[None | str] = None
    password: Union[None | str] = None

    is_add: bool = False



class PublishLogger:
    def __init__(self, redis: Redis, file_name: str):
        self.file_name = file_name
        self.redis: Redis = redis

    async def pub_log(self, send_data: str):
        try:
            self.file.write(send_data + '\n' if send_data[-1] != '\n' else '')

            await self.redis.publish(REDIS_PUBSUB_CHANNEL, send_data)
        except Exception as ex:
            logger.error(f'Fail to write data {send_data} - {str(ex)}')

    def __enter__(self):
        self.file = open(self.file_name, 'a', encoding='utf-8')
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        self.file.close()


class TelegramTasks:
    def __init__(self):

        # Хранилище Telegram аккаунтов в хэш таблице
        self.accounts_list = {}

    async def append_account(
            self,
            api_id: int,
            api_hash: str,
            session_name: str,
            db_id: type[int | None] = None
    ):
        """
        db_id: int - Уникальный идентификатор
        api_id: int - Апи ид для работы с mtproto
        api_hash: str - Хэш
        session_name: str - Название сессии
        """
        acc = telethon.TelegramClient(
            session=os.path.join('./', 'sessions', session_name),
            api_id=api_id,
            api_hash=api_hash
        )

        await acc.connect()

        tg_data = TelegramData(
            api_id=api_id,
            api_hash=api_hash,
            session_name=session_name,

            client=acc
        )

        logger.info(f'Added account to list - {db_id}')

        acc_key = db_id

        if db_id is None:
            acc_key = str(uuid.uuid4())

        # Добавление аккаунта в список
        self.accounts_list[acc_key] = tg_data

        return {'key': str(acc_key)}

    # Используется только для того, чтобы изменить данные
    async def telegram_data(self, db_id: type[str | int]) -> TelegramData:
        acc: TelegramData = self.accounts_list.get(db_id)

        if acc is None:
            return None

        return acc

    # Изменить название ключа при авторизации
    async def change_key(self, old_key: str, new_key: int) -> None:
        try:
            self.accounts_list[new_key] = self.accounts_list.pop(old_key)
        except Exception as ex:
            logger.error(f'Not swap keys - {str(ex)}')

    # Выход из аккаунтов
    async def disconnect_accounts(self):
        accounts_list: list[TelegramData] = self.accounts_list.values()

        for i in accounts_list:
            try:
                await i.client.disconnect()
            except Exception as ex:
                logger.error(f'Ошибка при выходе из аккаунта: {str(ex)}')

    async def exit_from_account(self, db_id: int):
        acc: TelegramData = self.accounts_list.get(db_id)

        if acc is None:
            return None
        
        self.accounts_list.pop(db_id)

        return True

    # Получить информацию об аккаунте
    async def get_account_info(self, db_id: int, redis: Redis,) -> type[None | InputPeerUser | User]:
        acc: TelegramData = self.accounts_list.get(db_id)

        if acc is None:
            return None
        
        cache_key = f"tg_account:{db_id}"
        cached_data = await redis.get(cache_key)

        if cached_data:
            # Return cached data if exists
            return json.loads(cached_data)

        acc_data = await acc.client.get_me()

        result = {
            'status': 'ok',
            'detail': {
                'user_id': acc_data.id,
                'username': acc_data.username,
                'fullname': f"{acc_data.first_name} {acc_data.last_name if acc_data.last_name else ''}"
            }
        }

        await redis.set(cache_key, json.dumps(result), ex=10800)

        return result

    async def check_user_auth(self, db_id: type[str | int]) -> bool:
        acc: TelegramData = self.accounts_list.get(db_id)

        if acc is None:
            return None

        data = await acc.client.is_user_authorized()
        # acc.client.set_proxy()
        # acc.client.rec
        return data
    
    async def set_proxy_client(self, db_id: type[str | int], proxy_data: tuple | None, redis: Redis) -> None:
        acc: TelegramData = self.accounts_list.get(db_id)

        if acc is None:
            return None

        data = await acc.client.is_user_authorized()
        if data:
            await acc.client.disconnect()

            await acc.client.set_proxy(proxy=proxy_data)
            await acc.client.connect()
        else:
            await acc.client.disconnect()

            await acc.client.set_proxy(proxy_data=())
            await acc.client.connect()
        

        cache_key = f"tg_account:{db_id}"
        # cached_data = await redis.get(cache_key)
        await redis.delete(cache_key)

        return data

    async def send_message_user(self, acc: telethon.TelegramClient, user_id, type_message: str = 'text', text_message: str = '', files: list[str] = []):
        if type_message == 'text':
            await acc.send_message(user_id, text_message)
        if type_message == 'text_and_media':
            await acc.send_file(user_id, files[0:9], caption=text_message)
        if type_message == 'video_note':
            await acc.send_file(user_id, files[0], video_note=True)
        if type_message == 'voice_note':
            await acc.send_file(user_id, files[0], voice_note=True)

    # Проверить сообщение в избранном
    async def check_message(self, db_id: int, type_message: str = 'text', text_message: str = '', files: list[str] = []):
        acc: TelegramData = self.accounts_list.get(db_id)

        if acc is None:
            return None

        if await acc.client.is_user_authorized():
            try:
                await self.send_message_user(acc.client, 'me', type_message, text_message, files)
            except Exception as ex:
                remove_files(files)
                return {'status': 'fail', 'detail': str(ex)}

            remove_files(files)
            return {'status': 'ok', 'detail': ''}
        else:
            remove_files(files)
            return {'status': 'fail', 'detail': 'user not auth'}

    # Отправить пуши...
    async def send_pushes(self, db_id: int, redis: Redis, type_db: str = 'fd', type_message: str = 'text', text_message: str = '', files: list[str] = [], limit: int = 10000, hours_limit: int = 0, limit_speed:str = 'max',  hours_limit_msg: float = 0, timezone: str = 'Europe/Moscow', job_id = None):
        acc: TelegramData = self.accounts_list.get(db_id)
        client: telethon.TelegramClient = acc.client

        if acc is None:
            return None

        limit = int(limit)

        limit_send_push = 0
        is_archived = True if type_db in ['rd', 'rd_pinned'] else False
        archive_users_ids = []
        me_data = await client.get_me()
        
        moscow_tz = pytz.timezone('Europe/Moscow')
        current_timezone = pytz.timezone(timezone)

        utc_time = datetime.now(tz=current_timezone)
        utc_time_with_desired_hour = utc_time.replace(hour=hours_limit_msg, minute=0, second=0, microsecond=0)
        current_time_with_timezone = utc_time_with_desired_hour


        with PublishLogger(redis, './static/logs/' + get_formatted_date_filename()) as f:
            if await client.is_user_authorized():

                utc_time = datetime.now(tz=datetime_timezone.utc)
                current_time = utc_time.replace(tzinfo=pytz.utc).astimezone(moscow_tz)
 
                await f.pub_log(
                    f'[{me_data.username}]: Начинаю рассылку для {type_db.upper()} базы. Время {current_time}'
                )  

                # TODO: собрать список с архива,  затем пушить fd базу..
                if type_db == 'fd':
                    await f.pub_log(
                        f'[{me_data.username}]: Сортурую диалоги...'
                    )  
                    async for user in client.iter_dialogs(limit=10000, archived=True):
                        if isinstance(user.draft.entity, telethon.types.User):
                            if not user.draft.entity.bot:
                                # Проверка на самого себя.
                                if not isinstance(user.input_entity, telethon.types.InputPeerSelf):
                                    archive_users_ids.append(user.draft.entity.id)
                    
                    await f.pub_log(
                        f'[{me_data.username}] Сортировка закончена'
                    )  


                async for user in client.iter_dialogs(limit=10000, archived=is_archived):
                    if isinstance(user.draft.entity, telethon.types.User):
                        if not user.draft.entity.bot:

                            # Проверка на самого себя.
                            if not isinstance(user.input_entity, telethon.types.InputPeerSelf):
                                
                                # Проверка на завершение работы
                                if job_id is not None:
                                    async with async_session() as session:
                                        async with session.begin():
                                            try:
                                                query = await session.execute(select(models.PushList).where(models.PushList.job_id == job_id))
                                                res = query.scalar_one_or_none()

                                                if res is not None:
                                                    if res.is_completed == True:
                                                        send_data = f'[{me_data.username}]: Остановлено'
                                                        await f.pub_log(send_data)
                                                        return {'status': 'ok', 'detail': ''}
                                            except:
                                                ...

                                                    
                                # Если диалог помечен как непрочитанный
                                if user.dialog.unread_mark == True:
                                    continue

                                if user.unread_count > 0:
                                    continue

                                if type_db == 'rd_pinned':
                                    if not user.pinned:
                                        continue
                                
                                if type_db == 'rd':
                                    if user.pinned:
                                        continue

                                if type_db == 'fd':
                                    if user.draft.entity.id in archive_users_ids:
                                        send_data = f'[{me_data.username}]: Диалог {user.draft.entity.first_name} в архиве'
                                        await f.pub_log(send_data)
                                        continue


                                session: AsyncSession
                                push_user = True
                                async with async_session() as session:
                                    async with session.begin():
                                        try:
                                            if is_archived:
                                               push_user = await add_or_update_user(session, models.RDusers, user, db_id, hours_limit)
                                            else:
                                                push_user = await add_or_update_user(session, models.FDusers, user, db_id, hours_limit)
                                        except Exception as ex:
                                            print('Ошибка при записи в таблицу: ', str(ex))

                                if not push_user:
                                    send_data = f'[{me_data.username}]: Юзеру {user.draft.entity.first_name} уже был отправлен пуш в течении {hours_limit} часов\n'
                                    await f.pub_log(send_data)
                                    continue

                                is_hours_limit_msg = False
                                hours_limit_msg = int(hours_limit_msg)
                                msg_from_user = datetime.now(tz=datetime_timezone.utc).astimezone(current_timezone)

                                # Если прошло меньше времени, с последнего отправленного сообщения не от бота
                                if hours_limit_msg > 0:
                                    if hours_limit_msg > 24:
                                        hours_limit_msg = 23

                                    # current_time_with_timezone

                                    async for msg in client.iter_messages(user.input_entity, limit=40):
                                        # Сообщение не пользователя
                                        if msg.peer_id.user_id != me_data.id:
                                            msg_from_user = msg.date.astimezone(current_timezone)
                                            
                                            if current_time_with_timezone < msg_from_user:
                                                is_hours_limit_msg = True
                                                break


                                if is_hours_limit_msg:
                                    send_data = f'[{me_data.username}]: Юзер {user.draft.entity.first_name} с id {user.draft.entity.id} написал сообщение, скип. {msg_from_user.strftime("%H:%M %d-%m-%Y")} - {hours_limit_msg}:00'
                                    await f.pub_log(send_data)
                                    continue

                                            

                                limit_send_push += 1
                                send_data = f'[{me_data.username}]: Отправляю пуш юзеру {user.draft.entity.first_name} с id {user.draft.entity.id}'
                                await f.pub_log(send_data)

                                try:
                                    await self.send_message_user(acc.client, user.input_entity, type_message, text_message, files)

                                    send_data = f'[{me_data.username}]: Отправил пуш юзеру {user.draft.entity.first_name} с id {user.draft.entity.id}'
                                    await f.pub_log(send_data)
                                except Exception as ex:
                                    send_data = f'[{me_data.username}]: Не удалось отправить пуш юзеру с id {user.draft.entity.id} {str(ex)}'
                                    await f.pub_log(send_data)

                                print(limit_speed)

                                if limit_speed != 'max':
                                    l_min = LIMIT_SPEED.get(limit_speed)[0]
                                    l_max = LIMIT_SPEED.get(limit_speed)[-1]
                                    if l_min and l_max:
                                        random_time = randint(l_min, l_max)
                                        send_data = f'[{me_data.username}]: Сплю {random_time} секунд'

                                        await f.pub_log(send_data)
                                        await asyncio.sleep(random_time)
                                    # await asyncio.sleep(randint(LIMIT_SPEED[limit_speed]))


                            if limit_send_push == limit:
                                break


                utc_time = datetime.utcnow()
                current_time = utc_time.replace(tzinfo=pytz.utc).astimezone(moscow_tz)
 
                send_data = f'[{me_data.username}]: Рассылка для {type_db.upper()} базы закончена. Время {current_time}\n'
                await f.pub_log(send_data)

                if job_id is not None:
                    async with async_session() as session:
                        async with session.begin():
                            try:
                                query = await session.execute(select(models.PushList).where(models.PushList.job_id == job_id))
                                res = query.scalar_one_or_none()

                                if res is not None:
                                    res.is_completed = True

                                await session.commit()
                            except Exception as ex:
                                print('Ошибка при записи в таблицу: ', str(ex))
            
            return {'status': 'ok', 'detail': ''}
    

    async def sign_in(self, db_id: int, code: str = '', password: str = '' ):
        acc: TelegramData = self.accounts_list.get(db_id)

        if acc is None:
            return None
        
        if code:
            await acc.client.sign_in(
                phone=acc.phone,
                code=code,
                password=password,
                phone_code_hash=acc.phone_hash
            )

        elif password:
            await acc.client.sign_in(password=password)



    
    async def send_phone(self, db_id: int, phone: str):
        acc: TelegramData = self.accounts_list.get(db_id)

        if acc is None:
            return None
        
        res = await acc.client.send_code_request(phone=phone, force_sms=False)
        acc.phone = phone
        acc.phone_hash = res.phone_code_hash

        return True

