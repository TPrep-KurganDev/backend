import time
import json
from datetime import datetime, timezone

from fastapi.params import Depends
from sqlalchemy.orm import Session
from pywebpush import webpush, WebPushException

from infrastructure.notification.notification import Notification
from infrastructure.database import get_db
from infrastructure.notification.notification_repo import NotificationRepo
from infrastructure.user.user import User
from config import VAPID_PUBLIC_KEY, VAPID_PRIVATE_KEY, VAPID_CLAIMS

BATCH_SIZE = 1000
INTERVAL_SECONDS = 300


def serialize_notification(notification: Notification):
    return {
        "id": notification.id,
        "user_id": notification.user_id,
        "exam_id": notification.exam_id,
        "time": notification.time.isoformat()
    }


def fetch_due_notifications(db: Session = Depends(get_db), batch_size: int = BATCH_SIZE):
    now = datetime.now(timezone.utc)
    query = db.query(Notification).filter(Notification.time >= now)

    for notif in query.yield_per(batch_size):
        yield notif


def send_push(user: User, notification_data: dict):
    if not user.push_key or not user.endpoint:
        return

    subscription_info = {
        "endpoint": user.endpoint,
        "keys": {
            "p256dh": user.push_key,
            "auth": user.auth_token
        }
    }

    try:
        webpush(
            subscription_info=subscription_info,
            data=json.dumps(notification_data),
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims=VAPID_CLAIMS
        )
        print(f"[{datetime.now()}] Sent notification {notification_data['id']} to user {user.id}")
    except WebPushException as e:
        print(f"[{datetime.now()}] Failed to send notification {notification_data['id']} to user {user.id}: {e}")


def process_notifications():
    with get_db() as session:
        for notification in fetch_due_notifications(session):
            user = session.query(User).filter(User.id == notification.user_id).first()
            if not user:
                continue

            data = serialize_notification(notification)
            send_push(user, data)

            NotificationRepo.delete_notification(notification.user_id, notification.exam_id, session)


def main_loop():
    while True:
        try:
            process_notifications()
        except Exception as e:
            print(f"[{datetime.now()}] Error in Notificator: {e}")
        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    print(f"[{datetime.now()}] Notificator started")
    main_loop()
