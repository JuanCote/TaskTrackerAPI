import os
from datetime import datetime

import pytz
from pymongo import MongoClient

from model.message_model import Message

timezone = pytz.timezone('Europe/Moscow')

MONGODB_URI = os.getenv('MONGODB_URI')
client = MongoClient(MONGODB_URI)
db = client.Sanyok

cards = db.cards
stats = db.stats
users = db.users
week_cards = db.week_cards
chat_rooms = db.chat_rooms


async def insert_message(message: Message):
    from utils.chat import encrypt_message

    dict_to_push = {'$push': {'messages': {
        'from': message.sender,
        'to': message.receiver,
        'message': encrypt_message(message.message),
        'time': message.date,
        'id': message.id
    }}}
    cursor = chat_rooms.find_one({'members': {'$all': [message.receiver, message.sender]}})
    if cursor is not None:
        chat_rooms.update_one({'members': {'$all': [message.receiver, message.sender]}}, dict_to_push)
    else:
        create_chat(message.sender, message.receiver)
        chat_rooms.update_one({'members': {'$all': [message.receiver, message.sender]}}, dict_to_push)


def create_chat(user, user2):
    chat_rooms.insert_one({
        'members': [user, user2],
        'messages': []
    })


def create_week_card(user):
    data = {
        'user': user,
        'cards': dict(),
        'last_checked': datetime.now(timezone)
    }
    days = ("monday", "tuesday", 'wednesday', 'thursday', 'friday', 'saturday', 'sunday')
    for i in range(0, len(days)):
        data['cards'].update({
            days[i]: {
                'tasks': [],
            }
        })
    try:
        week_cards.insert_one(data)
        return data
    except:
        return False


def check_week(user):
    week_card = week_cards.find_one({'user': user})
    check_date = week_card['last_checked']
    curr_week = datetime.now(timezone).strftime("%V")
    if not check_date.strftime("%V") == curr_week:
        pass
    else:
        week_card['last_checked'] = datetime.now(timezone)
        for el in week_card['cards'].items():
            for task in el[1]['tasks']:
                task['is_completed'] = False
        week_cards.update_one({'user': user}, {'$set': week_card})

    return week_card