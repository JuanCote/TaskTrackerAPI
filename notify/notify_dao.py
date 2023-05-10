import json

from db import users
from notify import Response, ErrorResponse, UserDevicePayload, MessagePayload
from fcm import fcm_scv


async def save_device_token(user_device: UserDevicePayload):
    users.update_one({'username': user_device.username}, {'$set': {'device_token': user_device.token}})


async def get_device_token(username: str):
    user = users.find_one({'username': username})
    return user['device_token']


async def send(message: MessagePayload):
    token = await get_device_token(message.username)
    batch_response = fcm_scv.send(message.message,
                                  message.notify.get('title'),
                                  message.notify.get('body'),
                                  token
                                  )
    errors_lst = []
    for v in batch_response.responses:
        if v.exception:
            error = {}
            cause_resp = v.exception.__dict__.get("_cause").__dict__
            cause_dict = json.loads(cause_resp.get("content").decode('utf-8'))
            # Preparing custom error response list
            error["status"] = cause_dict.get("error").get("status", None)
            error["code"] = cause_dict.get("error").get("code", None)
            error["error_code"] = cause_dict.get("error").get("details")[0].get('errorCode', None)
            error["cause"] = cause_dict.get("error").get("message", None)
            errors_lst.append(error)

    resp = Response(
        success_count=batch_response.success_count,
        message=f"sent message to {batch_response.success_count} device(s)",
        error=ErrorResponse(
            count=batch_response.failure_count,
            errors=errors_lst
        )
    )

    return resp