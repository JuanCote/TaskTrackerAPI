import os
from datetime import datetime

import pytz
from pymongo import MongoClient

timezone = pytz.timezone('Europe/Moscow')

MONGODB_URI = os.getenv('MONGODB_URI')
client = MongoClient(MONGODB_URI)
db = client.Sanyok

cards = db.cards
stats = db.stats
users = db.users
week_cards = db.week_cards
chat_rooms = db.chat_rooms


async def insert_message(receiver: str, sender: str, message: str):
    time_now = int(datetime.now().timestamp() * 1000)
    dict_to_push = {'$push': {'messages': {
        'from': sender,
        'to': receiver,
        'message': message,
        'time': time_now,
        'id': time_now
    }}}
    cursor = chat_rooms.find_one({'members': {'$all': [receiver, sender]}})
    if cursor is not None:
        chat_rooms.update_one({'members': {'$all': [receiver, sender]}}, dict_to_push)
    else:
        create_chat(sender, receiver)
        chat_rooms.update_one({'members': {'$all': [receiver, sender]}}, dict_to_push)
    return {'from': sender, 'to': receiver, 'message': message, 'time': time_now, 'id': time_now}


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