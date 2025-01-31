# main.py

from fastapi import FastAPI

import routers.authrouter
import routers.dbusers
import routers.logsrouter
import routers.pushrouter
import routers.tgrouter
import routers.proxyrouter


from fastapi.middleware.cors import CORSMiddleware

from fastapi.staticfiles import StaticFiles
import uvicorn
import routers



app = FastAPI()
api_path = FastAPI()


origins = [
    "http://localhost:2105",
    "http://localhost:3000",
]

# Добавление cors во все модели
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
api_path.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_path.include_router(
    router=routers.dbusers.router,
    prefix='/dbusers',
    tags=['DB Users']
)

api_path.include_router(
    router=routers.logsrouter.router,
    prefix='/logs',
    tags=['Logs']
)

api_path.include_router(
    router=routers.tgrouter.router,
    prefix='/telethon',
    tags=['Telethon']
)

api_path.include_router(
    router=routers.authrouter.router,
    prefix='/auth',
    tags=['Auth']
)

api_path.include_router(
    router=routers.pushrouter.router,
    prefix='/push',
    tags=['Push List']
)

api_path.include_router(
    router=routers.proxyrouter.router,
    prefix='/proxies',
    tags=['Proxy List']
)

app.mount('/api/v1', api_path)
app.mount('/static', StaticFiles(directory='static'), name='static')


if __name__ == '__main__':
    uvicorn.run('app:app', host='localhost', port=8000, reload=True)
