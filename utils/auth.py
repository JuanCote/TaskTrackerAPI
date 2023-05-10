from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
import os
from datetime import datetime, timedelta
from typing import Union, Any
from jose import jwt


ACCESS_TOKEN_EXPIRE_DAYS = 30
JWT_SECRET_KEY = os.environ.get('MOBILE_SECRET_CODE')
ALGORITHM = "HS256"

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


reuseable_oauth = OAuth2PasswordBearer(
    tokenUrl="/api/login",
    scheme_name="JWT"
)

def get_hashed_password(password: str):
    return password_context.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
    return password_context.verify(password, hashed_pass)


def create_access_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
    return encoded_jwt

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