from config import QUEUE_NAME
from arq.connections import RedisSettings
from database.database import async_session
from sqlalchemy.ext.asyncio import AsyncSession
from database import models
from sqlalchemy import select
import asyncio

from redis.asyncio import Redis
import tasks_list.telegram_worker
import logging

from database.tasks_models import TelegramTasks


logger = logging.getLogger(__name__)


def configure_logging() -> None:
    logging.config.dictConfig(
        {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'console': {
                    'class': 'logging.Formatter',
                    'datefmt': '%H:%M:%S',
                    'format': '%(levelname)s:\t\b%(asctime)s %(name)s:%(lineno)d %(message)s', # noqa
                },
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'formatter': 'console',
                },
            },
            'loggers': {
                'arq': {'handlers': ['console'], 'level': 'INFO', 'propagate': True}, # noqa
                __name__: {'handlers': ['console'], 'level': 'INFO', 'propagate': True}, # noqa
            },
        }
    )


async def startup(ctx):
    configure_logging()

    # Воркер для работы с аккаунтами
    telethon_worker: TelegramTasks = TelegramTasks()

    redis = Redis(host="localhost", port=6379, decode_responses=True)
    ctx['redis_client'] = redis
    ctx['telethon_worker'] = telethon_worker

    logger.info('Start up tasks server...')

    session: AsyncSession
    async with async_session() as session:
        async with session.begin():
            query = await session.execute(select(models.TelethonUser))
            res = query.scalars().all()

            if res is not None:
                logger.info('Found tg accounts')

                for account_data in res:
                    await telethon_worker.append_account(
                        db_id=account_data.id,
                        api_id=account_data.api_id,
                        api_hash=account_data.api_hash,
                        session_name=account_data.session_name
                    )
            else:
                logger.info('Not found tg accounts')


async def shutdown(ctx):
    telethon_worker: TelegramTasks = ctx['telethon_worker']
    redis_client: Redis = ctx['redis_client']

    await redis_client.close()
    await telethon_worker.disconnect_accounts()


class WorkerSettings:
    functions = [
        tasks_list.telegram_worker.get_account_info,
        tasks_list.telegram_worker.create_telethon_session,
        tasks_list.telegram_worker.send_phone_request,
        tasks_list.telegram_worker.sign_in,
        tasks_list.telegram_worker.send_push_message,
        tasks_list.telegram_worker.send_push_db_message,
        tasks_list.telegram_worker.exit_from_account,
        tasks_list.telegram_worker.set_proxy
    ]
    on_startup = startup
    redis_settings = RedisSettings()
    on_shutdown = shutdown
    job_timeout = 99999999999
    queue_name = QUEUE_NAME
