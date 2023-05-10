from fastapi import APIRouter
from starlette.responses import JSONResponse

from db import users
from model.auth_model import AuthUser
from utils.auth import get_hashed_password


router = APIRouter()


@router.post('/api/registration', tags=['auth'], responses={
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
    user['password'] = get_hashed_password(user['password'])
    users.insert_one(user)

    return JSONResponse(status_code=200, content={'message': 'registration completed successfully'})