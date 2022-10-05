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
    dict_to_push = {'$push': {'messages': {
        'from': sender,
        'to': receiver,
        'message': message,
        'time': int(datetime.now().timestamp() * 1000)
    }}}
    cursor = chat_rooms.find_one({'members': [receiver, sender]})
    if cursor is not None:
        chat_rooms.update_one({'members': [receiver, sender]}, dict_to_push)
    else:
        cursor = chat_rooms.find_one({'members': [sender, receiver]})
        if cursor is not None:
            chat_rooms.update_one({'members': [sender, receiver]}, dict_to_push)


def create_chat(user, user2):
    chat_rooms.insert_one({
        'members': [user, user2],
        'messages': []
    })

