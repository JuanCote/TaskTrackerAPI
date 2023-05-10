from typing import List

from firebase_admin import credentials, initialize_app, messaging


def init():
    cred = credentials.Certificate("credentials/key.json")
    initialize_app(cred)


def send(msg: str, title: str, body: str, token: str) -> messaging.BatchResponse:
    notification = messaging.Notification(
        title=title,
        body=body
    )

    message = messaging.send(
        data={"message": msg},
        token=token,
        notification=notification
    )
    try:
        # ``dry_run`` mode is enabled, the message will not be actually delivered to the
        # recipients.Instead FCM performs all the usual validations, and emulates the send operation.
        br = messaging.send(message, dry_run=True)
        # See the BatchResponse reference documentation
        # for the contents of response.
        return br
    except Exception as e:
        print('exception occur when sending message using firebase admin sdk')