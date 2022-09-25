import pymongo
import pytz
import os

from fastapi import FastAPI, Request
from pydantic import BaseModel, Field
from typing import Optional, Union
from datetime import datetime, timedelta
from bson.objectid import ObjectId
from starlette.responses import JSONResponse
from passlib.context import CryptContext
from jose import JWTError, jwt, ExpiredSignatureError

from db import cards, stats, users


app = FastAPI(docs_url="/")

timezone = pytz.timezone('Europe/Moscow')

SECRET_KEY = os.environ.get('mobile_secret_code')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30


class Card(BaseModel):
    title: str
    date: datetime
    counter: int


class UpdateCard(BaseModel):
    title: Optional[str]
    counter: Optional[int]
    date: datetime


class ResponseCard(BaseModel):
    id: str
    title: str
    date: datetime
    counter: int
    user: str


class AuthUser(BaseModel):
    username: str = Field(max_length=20, min_length=6)
    password: str = Field(max_length=30, min_length=6)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@app.get('/api/get_cards/{username}', tags=['cards'], responses={
    200: {
        'description': 'Gives back all cards',
        'content': {
            'application/json': {
                'example': {'list of cards'}
            }
        }
    },
    404: {
        'description': 'user not found',
        'content': {
            'application/json': {
                'example': {'message': 'user not found'}
            }
        }
    }
})
async def get_cards(access_token: str):
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        if username is None:
            return JSONResponse(status_code=401, content={'message': 'invalid token'})

    except ExpiredSignatureError:
        return JSONResponse(status_code=403, content="token has been expired")
    except JWTError:
        return JSONResponse(status_code=401, content={'message': 'invalid token'})

    if users.find_one({'username': username}) is None:
        return JSONResponse(status_code=404, content={'message': 'user not found'})
    cursor = cards.find({'is_deleted': False, 'user': username}).sort("date", pymongo.DESCENDING)

    result = []

    for card in cursor:
        card['id'] = str(card['_id'])  # converting id from ObjectId to string

        current_time = datetime.now(timezone).replace(tzinfo=None)

        difference = int((current_time - card['viewed']).total_seconds() // 3600)
        if difference > 24 or current_time.day != card['viewed'].day:
            stats.update_one({'card': str(card['_id'])}, {'$set': {str(card['viewed'].strftime('%Y-%m-%d')): card['counter']}})
            delta = current_time - card['viewed']
            if delta.days > 1:
                data_update = dict()
                for i in range(1, delta.days):
                    day = datetime.strftime(card['viewed'] + timedelta(days=i), '%Y-%m-%d')
                    data_update.update({day: 0})
                stats.update_one({'card': str(card['_id'])}, {'$set': data_update})

            card['counter'] = 0
            cards.update_one({'_id': card['_id']}, {'$set': {'counter': 0}})

        cards.update_one({'_id': card['_id']}, {'$set': {'viewed': current_time}})

        del card['is_deleted'], card['_id'], card['viewed']
        result.append(card)

    return result


@app.post('/api/add_card/{access_token}', tags=['cards'], response_model=ResponseCard)
async def add_card(card: Card, access_token: str):
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        if username is None:
            return JSONResponse(status_code=401, content={'message': 'invalid token'})

    except ExpiredSignatureError:
        return JSONResponse(status_code=403, content="token has been expired")
    except JWTError:
        return JSONResponse(status_code=401, content={'message': 'invalid token'})

    if users.find_one({'username': username}) is None:
        return JSONResponse(status_code=404, content={'message': 'user not found'})

    card = card.dict()
    card['is_deleted'] = False
    card['user'] = username
    card['viewed'] = datetime.now(timezone)
    cards.insert_one(card)

    card['id'] = str(card['_id'])  # converting id from ObjectId to string
    del card['is_deleted'], card['_id'], card['viewed']

    stat = {
        'card': card['id']
    }
    stats.insert_one(stat)

    return card


@app.delete(
    '/api/delete_card/{card_id}/{access_token}', tags=['cards'],
    responses={
        404: {
            "description": "The card was not found",
            "content": {
                "application/json": {
                    "example": {"message": "non-existent card"}
                }
            }
        },
        200: {
            "description": "Successful removal",
            "content": {
                "application/json": {
                    "example": {"message": "deleted"}
                }
            },
        },
    },
)
async def delete_card(card_id: str, access_token: str):
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        if username is None:
            return JSONResponse(status_code=401, content={'message': 'invalid token'})

    except ExpiredSignatureError:
        return JSONResponse(status_code=403, content="token has been expired")
    except JWTError:
        return JSONResponse(status_code=401, content={'message': 'invalid token'})

    if users.find_one({'username': username}) is None:
        return JSONResponse(status_code=404, content={'message': 'user not found'})

    try:
        cards.update_one({'_id': ObjectId(card_id)}, {'$set': {'is_deleted': True}})
    except:
        return JSONResponse(status_code=404, content={'message': 'non-existent card'})

    return {"message": "deleted"}


@app.put('/api/update_card/{card_id}/{access_token}', tags=['cards'], response_model=ResponseCard, responses={
    404: {
        "description": "The card was not found",
        "content": {
            "application/json": {
                "example": {'message': 'non-existent card'}
            }
        }
    }
})
async def update_card(card_id: str, access_token: str, card: UpdateCard):
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        if username is None:
            return JSONResponse(status_code=401, content={'message': 'invalid token'})

    except ExpiredSignatureError:
        return JSONResponse(status_code=403, content="token has been expired")
    except JWTError:
        return JSONResponse(status_code=401, content={'message': 'invalid token'})

    if users.find_one({'username': username}) is None:
        return JSONResponse(status_code=404, content={'message': 'user not found'})

    card = card.dict(exclude_unset=True)  # getting a dictionary with only the entered fields

    try:
        cards.update_one({'_id': ObjectId(card_id)}, {'$set': card})
    except:
        return JSONResponse(status_code=404, content={'message': 'non-existent card'})

    new_card = cards.find_one(ObjectId(card_id))

    new_card['id'] = str(new_card['_id'])
    del new_card['_id'], new_card['is_deleted'], new_card['viewed']

    return new_card


@app.get('/api/get_stat/{card_id}', tags=['cards'], responses={
    404: {
        "description": "The card was not found",
        "content": {
            "application/json": {
                "example": {'message': 'non-existent card'}
            }
        }
    },
    200: {
        'description': 'Gives back all cards',
        'content': {
            'application/json': {
                'example': {'list of stat'}
            }
        }
    }
})
async def get_stat(card_id: str):
    stat = stats.find_one({'card': card_id})
    if stat is None:
        return JSONResponse(status_code=404, content={'message': 'non-existent card'})

    del stat['_id'], stat['card']

    result = []
    for key, value in stat.items():
        result.append({'date': key, 'counter': value})

    print(result)

    return result


@app.post('/api/registration', tags=['auth'], responses={
    409: {
        "description": "User already exists",
        "content": {
            "application/json": {
                "example": {'message': 'nickname is taken'}
            }
        }
    },
    200: {
        'description': 'Registration completed successfully',
        'content': {
            'application/json': {
                'example': {'message': 'registration completed successfully'}
            }
        }
    }
})
async def registration(user: AuthUser):
    if users.find_one({'username': user.username}) is not None:
        return JSONResponse(status_code=409, content={'message': 'nickname is taken'})

    user = user.dict()
    user['password'] = get_password_hash(user['password'])
    users.insert_one(user)

    return JSONResponse(status_code=200, content={'message': 'registration completed successfully'})


@app.post('/api/login', tags=['auth'], responses={
    404: {
        "description": "User not found",
        "content": {
            "application/json": {
                "example": {'message': 'user not found'}
            }
        }
    },
    200: {
        'description': 'Login completed successfully',
        'content': {
            'application/json': {
                'example': {'access_token': 'string of token', 'username': 'string'}
            }
        }
    },
    401: {
        'description': 'Wrong password',
        'content': {
            'application/json': {
                'example': {'message': 'wrong password'}
            }
        }
    }
})
async def login(user: AuthUser):
    data_user = users.find_one({'username': user.username})
    if data_user is None:
        return JSONResponse(status_code=404, content={'message': 'user not found'})

    if not verify_password(user.password, data_user['password']):
        return JSONResponse(status_code=401, content={'message': 'wrong password'})

    access_token_expires = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    access_token = create_access_token(data={'username': user.username}, expires_delta=access_token_expires)

    return JSONResponse(status_code=200, content={
        'access_token': access_token,
        'username': user.username
    })


@app.get('/api/get_current_user/{access_token}', tags=['auth'], responses={
    200: {
        'description': 'Login completed successfully',
        'content': {
            'application/json': {
                'example': {'username': 'string'}
            }
        }
    },
    401: {
        'description': 'Wrong password',
        'content': {
            'application/json': {
                'example': {'message': 'invalid token'}
            }
        }
    },
    403: {
        'description': 'Token expired',
        'content': {
            'application/json': {
                'example': {'message': 'token has been expired'}
            }
        }
    }
})
async def get_current_user(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        if username is None:
            return JSONResponse(status_code=401, content={'message': 'invalid token'})

        return JSONResponse(status_code=200, content={'username': username})
    except ExpiredSignatureError:
        return JSONResponse(status_code=403, content="token has been expired")
    except JWTError:
        return JSONResponse(status_code=401, content={'message': 'invalid token'})
