from fastapi import APIRouter, Depends
import glob
import os

from arq import ArqRedis
from tools import (
    TokenData,
    get_current_user,
    get_arq_connection,
    get_files_from_folder
)

router = APIRouter()



@router.get("/get_files_logs")
async def check_push_message(
    current_user: TokenData = Depends(get_current_user),
    arq: ArqRedis = Depends(get_arq_connection),
):
    files = get_files_from_folder('./static/logs')

    return files



@router.delete("/delete_logs")
async def check_push_message(
    current_user: TokenData = Depends(get_current_user),
    arq: ArqRedis = Depends(get_arq_connection),
):
    try:
        files = glob.glob('./static/logs/*')

        for i in files:
            os.remove(i)
    except Exception as ex:
        return {'status': 'fail', 'detail': str(ex)}

    return {'status': 'ok', 'detail': ''}