from datetime import datetime
from pymongo import MongoClient

MONGODB_URI = 'mongodb+srv://JuanCote:tfkn7C64u55PFtl4@cluster0.lecracw.mongodb.net/?retryWrites=true&w=majority'
client = MongoClient(MONGODB_URI)
db = client.Sanyok

cards = db.cards
stats = db.stats
users = db.users
chat_rooms = db.chat_rooms


def insert_message(receiver: str, sender: str, message: str):
    time_now = int(datetime.now().timestamp() * 1000)
    dict_to_push = {'$push': {'messages': {
        'from': sender,
        'to': receiver,
        'message': message,
        'time': time_now
    }}}
    cursor = chat_rooms.find_one({'members': {'$all': [receiver, sender]}})
    if cursor is not None:
        chat_rooms.update_one({'members': {'$all': [receiver, sender]}}, dict_to_push)
    else:
        create_chat(sender, receiver)
        chat_rooms.update_one({'members': {'$all': [receiver, sender]}}, dict_to_push)
    return {'sender': sender, 'message': message, 'time': time_now}


def create_chat(user, user2):
    chat_rooms.insert_one({
        'members': [user, user2],
        'messages': []
    })

