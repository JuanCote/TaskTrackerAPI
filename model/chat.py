from db import chat_rooms


async def chat_users(user):
    chats = chat_rooms.find({'members': {'$all': [user]}}, {'_id': 0})

    data = list()
    for chat in chats:
        last_message = chat['messages'][-1]  # last chat message
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
