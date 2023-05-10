from fastapi import Depends, APIRouter
from starlette.responses import JSONResponse

from db import users
from model.auth_model import AuthUser
from utils.auth import verify_password, create_access_token, get_current_user


router = APIRouter()

@router.post('/api/login', tags=['auth'], responses={
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
                'example': {'access_token': 'string of token'}
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

    return JSONResponse(status_code=200, content={
        "access_token": create_access_token(user.username)
    })


@router.get('/api/get_current_user', tags=['auth'], responses={
    200: {
        'description': 'Success login',
        'content': {
            'application/json': {
                'example': {'username': 'string'}
            }
        }
    },
    401: {
        'description': 'Not authenticated',
        'content': {
            'application/json': {
                'example': {"detail": "Not authenticated"}
            }
        }
    },
})
async def me(user: str = Depends(get_current_user)):
    return {'username': user}