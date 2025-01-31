# TG-Newsletter
![Настройка рассылки](https://i.imgur.com/F3J40kz.png)

![Действия с аккаунтами](https://i.imgur.com/1igkAh2.png)

Телеграм бот для рассылки по личным сообщениям с Веб Панелью.

Поддержка множества аккаунтов, рассылка в определенное время и поддержка socks5 прокси, и разных типов сообщений.

## Содержание
- [Технологии](#технологии)
- [Использование](#использование)
- [Тестирование](#тестирование)


## Технологии
- [Vue](https://vuejs.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Telethon](https://github.com/LonamiWebs/Telethon)
- [Arq](https://github.com/python-arq/arq)

## Использование
Создать виртуальное окружение:
```sh
python3 -m venv venv
source venv/bin/activate
```
Установить зависимости:
```sh
pip install -r requirements.txt
```

Применить миграции
```sh
alembic upgrade head
```

Затем настроить supervisor конфиг для 3 файлов api.conf, arq.conf и ws.conf

## FAQ 
Один из примеров проекта, который делал на заказ. Делалось всё на скорую руку, поэтому в большинстве мест код не очень хороший.


