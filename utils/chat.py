from db import chat_rooms


KEY = 7


def get_messages_from_chat(cursor):
    data = []
    for item in cursor['messages']:
        data.append(item)
    return data


def encrypt_message(text):
    encrypted = ""
    for char in text:
        encrypted += chr(ord(char) + KEY)
    return encrypted


def decrypt_message(encrypted_text):
    decrypted = ""
    for char in encrypted_text:
        decrypted += chr(ord(char) - KEY)
    return decrypted


async def chat_users(user):
    chats = chat_rooms.find({'members': {'$all': [user]}}, {'_id': 0})

    data = list()
    for chat in chats:
        last_message = chat['messages'][-1].copy()  # last chat message
        if last_message['from'] == user:
            last_message['is_myself'] = True
        else:
            last_message['is_myself'] = False
        del last_message['from'], last_message['to']
        data.append({
            'username': [el for el in chat['members'] if el != user][0],  # who is chatting with
            'last_message': last_message, 'messages': chat['messages']

        })

    return data
