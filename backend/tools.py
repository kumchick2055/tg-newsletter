from datetime import datetime
import config
import jwt
from datetime import timedelta
from fastapi import HTTPException, status, Depends
from pydantic import BaseModel
from typing import Optional

import bcrypt
import argparse
from fastapi.security import OAuth2PasswordBearer
import os

from arq import create_pool
from arq.connections import RedisSettings
import uuid

from typing import List
from fastapi import UploadFile
from pathlib import Path
import re

import python_socks



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


class TokenData(BaseModel):
    username: Optional[str] = None



def parse_socks5_uri(uri):
    # Регулярное выражение для парсинга URI
    pattern = r'socks5://(?:(?P<username>[^:]+):(?P<password>[^@]+)@)?(?P<address>[^:]+):(?P<port>\d+)'
    match = re.match(pattern, uri)

    if match:
        username = match.group('username') if match.group('username') else ''
        password = match.group('password') if match.group('password') else ''
        address = match.group('address')
        port = int(match.group('port'))
        
        if username != '' and password != '':
            return (python_socks.ProxyType.SOCKS5, username, password)
        return (python_socks.ProxyType.SOCKS5, username, password, True, address, port)
    else:
        raise ValueError("Invalid SOCKS5 URI")
    

async def get_arq_connection():
    arq = await create_pool(
        RedisSettings(),
        default_queue_name=config.QUEUE_NAME
    )
    yield arq


# Создает директорию, если она не существует
def ensure_tmp_directory_exists(directory: str = './tmp_files'):
    
    if not os.path.exists(directory):
        os.makedirs(directory)


# Сохраняет файлы во временную директорию и возвращает список путей к этим файлам
async def save_files_to_tmp(files_list: List[UploadFile], directory: str = './tmp_files') -> List[str]:

    saved_file_paths = []
    ensure_tmp_directory_exists(directory)

    for file in files_list:
        unique_filename = f"{uuid.uuid4()}{Path(file.filename).suffix}"
        file_path = os.path.join(directory, unique_filename)
        
        with open(file_path, "wb") as f:
            f.write(await file.read())
        
        saved_file_paths.append(file_path)
    
    return saved_file_paths




def get_files_from_folder(folder_path):
    # Получение всех названий файлов с расширением в указанной папке
    file_names = [file for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file))]
    
    return file_names


def remove_files(files):
    for i in files:
        try:
            os.remove(i)
        except:
            ...

def get_formatted_date_filename():

    # Получаем текущую дату
    current_datetime = datetime.now()

    # Форматируем дату в виде день_месяц_год
    formatted_date = current_datetime.strftime('%d_%m_%Y')

    # Добавляем расширение .txt и возвращаем результат
    return f'{formatted_date}.txt'



def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(), salt)
    return hashed_password.decode()



def check_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password.encode())



def create_jwt_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=999999) 
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm='HS256')
    return encoded_jwt


def verify_jwt_token(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=['HS256'])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    return token_data



async def get_current_user(token: str = Depends(oauth2_scheme)):
    return verify_jwt_token(token)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Hash a password using bcrypt.')
    parser.add_argument('--hash-password', type=str, help='Password to hash')
    parser.add_argument('--check-password', type=str, help='Password to check')
    parser.add_argument('--hashed-password', type=str, help='Hashed password to verify against')

    args = parser.parse_args()

    if args.hash_password:
        hashed = hash_password(args.hash_password)
        print(f'Hashed password: {hashed}')
    
    if args.check_password and args.hashed_password:
        if check_password(args.check_password, args.hashed_password):
            print("Password matches the hash.")
        else:
            print("Password does not match the hash.")