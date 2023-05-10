import pymongo
from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect, HTTPException

from datetime import datetime, timedelta
from bson.objectid import ObjectId
from starlette.responses import JSONResponse, HTMLResponse

from routers import card_router, login_router, register_router, socket_router
from socket_manager import manager
from db import cards, stats, users, chat_rooms, create_chat, week_cards, create_week_card, timezone, check_week
from utils.auth import get_current_user
from utils.chat import get_messages_from_chat
from fcm import fcm_scv

app = FastAPI(docs_url="/")

app.include_router(card_router.router)
app.include_router(login_router.router)
app.include_router(register_router.router)
app.include_router(socket_router.router)

fcm_scv.init()


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
async def get_stat(card_id: str, user: str = Depends(get_current_user)):
    stat = stats.find_one({'card': card_id})
    if stat is None:
        return JSONResponse(status_code=404, content={'message': 'non-existent card'})

    del stat['_id'], stat['card']

    result = []
    for key, value in stat.items():
        result.append({'date': key, 'counter': value})

    return result


@app.get('/api/get_chat/{user2}', tags=['chat'], responses={
    200: {
        'description': 'Gives all messages of selected chat',
        'content': {
            'application/json': {
                'example': [{
                    "from": "killer",
                    "to": "Nikita",
                    "message": "+"
                }, {
                    "from": "killer",
                    "to": "Nikita",
                    "message": "+"
                }]
            }
        }
    },
})
async def get_chat(user2: str, user: str = Depends(get_current_user)):
    cursor = chat_rooms.find_one({'members': {'$all': [user, user2]}})
    if cursor is None:
        return JSONResponse(status_code=200, content=[])
    else:
        data = get_messages_from_chat(cursor)

    return JSONResponse(status_code=200, content=data)


@app.get('/api/chat_search/{search}', tags=['chat'], responses={
    200: {
        'description': 'Return a list of users',
        'content': {
            'application/json': {
                'example': [
                    {
                        "username": "killer"
                    },
                    {
                        "username": "e.v.kartashova"
                    }
                ]
            }
        }
    },
})
async def search_chat(search: str, user: str = Depends(get_current_user)):
    return list(users.find({'username': {'$regex': search, '$options': 'i', '$ne': user}}, {'_id': 0, 'password': 0}))


# @app.get('/api/get_week_cards', tags=['week_card'], responses={
#     200: {
#         'description': 'Returns today`s week card',
#         'content': {
#             'application/json': {
#                 'example': [
#                     {
#                         "monday": {
#                             "tasks": [
#                                 {
#                                     "is_completed": False,
#                                     "task": "asdasd"
#                                 }
#                             ]
#                         }
#                     }
#                 ]
#             }
#         }
#     },
# })
# async def get_week_cards(user: str = Depends(get_current_user)):
#     week_card = week_cards.find_one({'user': user})
#     if week_card is None:
#         week_card = create_week_card(user)
#         if not week_card:
#             raise HTTPException(status_code=500, detail="DB error")
#     else:
#         week_card = check_week(user)
#
#     week_day = datetime.now(timezone).weekday()
#     today_card = list(week_card['cards'].items())[week_day]
#     data = {today_card[0]: today_card[1]}
#
#     return JSONResponse(status_code=200, content=data)


# @app.get('/api/get_all_week_cards', tags=['week_card'], responses={
#     200: {
#         'description': 'Returns all week cards',
#         'content': {
#             'application/json': {
#                 'example': [
#                     [
#                         {
#                             "monday": {
#                                 "tasks": [
#                                     {
#                                         "is_completed": False,
#                                         "task": "asdasd"
#                                     }
#                                 ]
#                             }
#                         },
#                         {
#                             "tuesday": {
#                                 "tasks": []
#                             }
#                         },
#                         {
#                             "wednesday": {
#                                 "tasks": []
#                             }
#                         },
#                         {
#                             "thursday": {
#                                 "tasks": []
#                             }
#                         },
#                         {
#                             "friday": {
#                                 "tasks": []
#                             }
#                         },
#                         {
#                             "saturday": {
#                                 "tasks": []
#                             }
#                         },
#                         {
#                             "sunday": {
#                                 "tasks": []
#                             }
#                         }
#                     ]
#                 ]
#             }
#         }
#     },
# })
# async def get_all_week_cards(user: str = Depends(get_current_user)):
#     week_card = week_cards.find_one({'user': user})
#     if week_card is None:
#         week_card = create_week_card(user)
#         if not week_card:
#             raise HTTPException(status_code=500, detail="DB error")
#     else:
#         week_card = check_week(user)
#
#     data = list()
#     for key, value in week_card['cards'].items():
#         data.append({key: value})
#
#     return JSONResponse(status_code=200, content=data)
#
#
# @app.post('/api/change_week_card', tags=['week_card'])
# async def change_week_card(user: str = Depends(get_current_user)):
#     pass

