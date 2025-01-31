from fastapi import APIRouter, status
from pydantic import BaseModel
from tools import check_password, create_jwt_token
from fastapi.exceptions import HTTPException

import config



router = APIRouter()

class LoginData(BaseModel):
    login: str
    password: str



@router.post("/login")
async def login(login_data: LoginData):

    if login_data.login != 'admin' or not check_password(login_data.password, config.ADMIN_PASSWORD):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль"
        )
    
    token_data = {"sub": login_data.login}
    token = create_jwt_token(token_data)
    return {"access_token": token, "token_type": "bearer"}
