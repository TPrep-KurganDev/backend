import time
from datetime import datetime, timezone
from typing import Any, Generator

from sqlalchemy.orm import Session
from pywebpush import webpush, WebPushException

from tprep.app.requests_models import Notification
from tprep.infrastructure.notification.notificationdb import NotificationDB
from tprep.infrastructure.database import get_db
from tprep.infrastructure.notification.notification_repo import NotificationRepo
from tprep.infrastructure.user.user import User
from config import settings

BATCH_SIZE = 1000
INTERVAL_SECONDS = 300


def fetch_due_notifications(
    db: Session, batch_size: int = BATCH_SIZE
) -> Generator[Notification, Any, None]:
    now = datetime.now(timezone.utc)
    query = db.query(NotificationDB).filter(NotificationDB.time >= now)

    for notif in query.yield_per(batch_size):
        yield Notification.from_db_model(notif)


def send_push(user: User, notification: Notification) -> None:
    if not user.push_key or not user.endpoint:
        return

    subscription_info = {
        "endpoint": user.endpoint,
        "keys": {"p256dh": user.push_key, "auth": user.auth_token},
    }

    try:
        webpush(
            subscription_info=subscription_info,
            data=notification.model_dump_json(),
            vapid_private_key=settings.VAPID_PRIVATE_KEY,
            vapid_claims=settings.VAPID_CLAIMS,
        )
        print(
            f"[{datetime.now()}] Sent notification {notification.id} to user {user.id}"
        )
    except WebPushException as e:
        print(
            f"[{datetime.now()}] Failed to send notification {notification.id} to user {user.id}: {e}"
        )


def process_notifications() -> None:
    # TODO поправить костыль с бдшкой и использовать собственный метод для получения юзера
    db_gen = get_db()
    session = next(db_gen)
    try:
        for notification in fetch_due_notifications(session):
            user = session.query(User).filter(User.id == notification.user_id).first()
            if not user:
                continue

            send_push(user, notification)

            NotificationRepo.delete_notification(
                notification.user_id, notification.exam_id, session
            )
    finally:
        next(db_gen, None)


def main_loop() -> None:
    while True:
        try:
            process_notifications()
        except Exception as e:
            print(f"[{datetime.now()}] Error in Notificator: {e}")
        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    print(f"[{datetime.now()}] Notificator started")
    main_loop()
