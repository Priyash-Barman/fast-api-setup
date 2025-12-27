import firebase_admin
from firebase_admin import credentials, messaging
from typing import Dict, Any, Optional
from fast_app.utils.logger import logger

from config import (
    FIREBASE_CLIENT_EMAIL,
    FIREBASE_PRIVATE_KEY,
    FIREBASE_PROJECT_ID,
)


# ------------------------------------------------
# Firebase Initialization (Only Once)
# ------------------------------------------------
def initialize_firebase() -> None:
    try:
        firebase_admin.get_app()
        return
    except ValueError:
        pass  # Not initialized yet

    cred = credentials.Certificate({
        "type": "service_account",
        "project_id": FIREBASE_PROJECT_ID,
        "client_email": FIREBASE_CLIENT_EMAIL,
        "private_key": FIREBASE_PRIVATE_KEY.replace("\\n", "\n"),
        "token_uri": "https://oauth2.googleapis.com/token",
    })

    firebase_admin.initialize_app(cred)
    logger.info("Firebase initialized")


# ------------------------------------------------
# Send Single Push Notification
# ------------------------------------------------
async def send_notification(
    *,
    token: str,
    title: str,
    body: str,
    data: Optional[Dict[str, Any]] = None,
) -> bool:
    """
    Send a single push notification using Firebase FCM.
    """

    try:
        initialize_firebase()

        message = messaging.Message(
            token=token,
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data={k: str(v) for k, v in (data or {}).items()},
        )

        messaging.send(message)
        return True

    except messaging.UnregisteredError:
        logger.warning(f"Invalid FCM token: {token}")
        return False

    except Exception as e:
        logger.exception("Failed to send push notification")
        return False


# ---------------------------------------------
# call send push notification function
# ---------------------------------------------
'''
await send_notification(
    token="fJDRWQTiQ5Vdfsrx7zmaRh:APA91bGoe1hGZyNIxNIsBkBGvh1l2055RGJB_1AckrnEwjFvQWBwLLgpEp8KhhTrIjNE5Hg63z5_9BoVVMlbh6PfpF4Bizl7hCt8tWD10YHQSHldPiWwn-s",
    title="Hello 👋",
    body="This is a test notification",
    data={"type": "TEST"},
)
'''