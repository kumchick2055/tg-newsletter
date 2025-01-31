
# Хэшированный пароль
# Для генерации пароля делать следующее:
# python tools.py --hash-password password

import os

from dotenv import load_dotenv
load_dotenv()


ADMIN_PASSWORD = os.environ['ADMIN_PASSWORD']
SECRET_KEY = os.environ['SECRET_KEY']

DATABASE_PATH = os.environ['DATABASE_PATH']

QUEUE_NAME = os.environ['QUEUE_NAME']
REDIS_PUBSUB_CHANNEL = os.environ['REDIS_PUBSUB_CHANNEL']

# Лимит по скорости пушей
LIMIT_SPEED = {
    "min": (1,3),
    "medium": (2,4),
    "slow": (6,14)
}