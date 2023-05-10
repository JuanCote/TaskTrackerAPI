from datetime import datetime, timedelta

import pymongo
from bson import ObjectId
from fastapi import Depends, APIRouter
from starlette.responses import JSONResponse

from db import users, cards, timezone, stats
from model.card_model import ResponseCard, Card, UpdateCard
from utils.auth import get_current_user


router = APIRouter()


@router.get('/api/get_cards', tags=['cards'], responses={
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
async def get_cards(user: str = Depends(get_current_user)):
    if users.find_one({'username': user}) is None:
        return JSONResponse(status_code=404, content={'message': 'user not found'})
    cursor = cards.find({'is_deleted': False, 'user': user}).sort("date", pymongo.DESCENDING)

    result = []

    for card in cursor:
        card['id'] = str(card['_id'])  # converting id from ObjectId to string

        current_time = datetime.now(timezone).replace(tzinfo=None)

        difference = int((current_time - card['viewed']).total_seconds() // 3600)
        if difference > 24 or current_time.day != card[
            'viewed'].day:  # checking on different days and adding to statistics
            stats.update_one({'card': str(card['_id'])},
                             {'$set': {str(card['viewed'].strftime('%Y-%m-%d')): card['counter']}})
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


@router.post('/api/add_card', tags=['cards'], response_model=ResponseCard)
async def add_card(card: Card, user: str = Depends(get_current_user)):
    if users.find_one({'username': user}) is None:
        return JSONResponse(status_code=404, content={'message': 'user not found'})

    card = card.dict()
    card['is_deleted'] = False
    card['user'] = user
    card['viewed'] = datetime.now(timezone)
    cards.insert_one(card)

    card['id'] = str(card['_id'])  # converting id from ObjectId to string
    del card['is_deleted'], card['_id'], card['viewed']

    stat = {
        'card': card['id']
    }
    stats.insert_one(stat)

    return card


@router.delete(
    '/api/delete_card/{card_id}', tags=['cards'],
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
async def delete_card(card_id: str, user: str = Depends(get_current_user)):
    if users.find_one({'username': user}) is None:
        return JSONResponse(status_code=404, content={'message': 'user not found'})

    try:
        cards.update_one({'_id': ObjectId(card_id), 'user': user}, {'$set': {'is_deleted': True}})
    except:
        return JSONResponse(status_code=404, content={'message': 'non-existent card'})

    return {"message": "deleted"}


@router.put('/api/update_card/{card_id}', tags=['cards'], response_model=ResponseCard, responses={
    404: {
        "description": "The card was not found",
        "content": {
            "application/json": {
                "example": {'message': 'non-existent card'}
            }
        }
    }
})
async def update_card(card_id: str, card: UpdateCard, user: str = Depends(get_current_user)):
    if users.find_one({'username': user}) is None:
        return JSONResponse(status_code=404, content={'message': 'user not found'})

    card = card.dict(exclude_unset=True)  # getting a dictionary with only the entered fields

    try:
        cards.update_one({'_id': ObjectId(card_id), 'user': user}, {'$set': card})
    except:
        return JSONResponse(status_code=404, content={'message': 'non-existent card'})

    new_card = cards.find_one(ObjectId(card_id))

    new_card['id'] = str(new_card['_id'])
    del new_card['_id'], new_card['is_deleted'], new_card['viewed']

    return new_card