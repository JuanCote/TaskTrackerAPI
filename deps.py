from typing import Union, Any
from datetime import datetime
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from utils import ALGORITHM, JWT_SECRET_KEY


from jose import jwt, ExpiredSignatureError, JWTError
from pydantic import ValidationError


reuseable_oauth = OAuth2PasswordBearer(
    tokenUrl="/api/login",
    scheme_name="JWT"
)


async def get_current_user(token: str = Depends(reuseable_oauth)):
    return await decode_token(token)


async def decode_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        return username
    except:
        return False
    # except ExpiredSignatureError:
    #     # raise HTTPException(
    #     #     status_code=status.HTTP_401_UNAUTHORIZED,
    #     #     detail="Token expired",
    #     #     headers={"WWW-Authenticate": "Bearer"},
    #     # )
    # except JWTError:
    #     pass
    #     # raise HTTPException(
    #     #     status_code=status.HTTP_403_FORBIDDEN,
    #     #     detail="Could not validate credentials",
    #     #     headers={"WWW-Authenticate": "Bearer"},
    #     # )