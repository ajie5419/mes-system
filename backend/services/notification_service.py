from typing import Optional, List
from sqlalchemy.orm import Session
from models.notification import Notification
from services.ws_service import manager
import logging

logger = logging.getLogger(__name__)


def create_notification(
    db: Session, user_id: int, title: str, content: str = "", type: str = "info",
    resource_type: str = None, resource_id: int = None
) -> Notification:
    n = Notification(
        user_id=user_id, title=title, content=content, type=type,
        related_resource_type=resource_type, related_resource_id=resource_id,
    )
    db.add(n)
    db.commit()
    db.refresh(n)
    # Real-time push via WebSocket
    try:
        import asyncio
        loop = asyncio.get_running_loop()
        loop.create_task(manager.broadcast_to_user(user_id, {
            "type": type,
            "data": {"id": n.id, "title": title, "content": content, "resource_type": resource_type, "resource_id": resource_id}
        }))
    except RuntimeError:
        pass  # no event loop
    return n


def create_batch_notifications(
    db: Session, user_ids: List[int], title: str, content: str = "", type: str = "info",
    resource_type: str = None, resource_id: int = None
) -> List[Notification]:
    notifications = []
    for uid in user_ids:
        n = Notification(
            user_id=uid, title=title, content=content, type=type,
            related_resource_type=resource_type, related_resource_id=resource_id,
        )
        db.add(n)
        notifications.append(n)
    db.commit()
    return notifications


def get_user_notifications(
    db: Session, user_id: int, unread_only: bool = False, page: int = 1, page_size: int = 20
):
    query = db.query(Notification).filter(Notification.user_id == user_id)
    if unread_only:
        query = query.filter(Notification.is_read == False)
    total = query.count()
    items = query.order_by(Notification.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return total, items


def mark_as_read(db: Session, notification_id: int, user_id: int) -> bool:
    n = db.query(Notification).filter(Notification.id == notification_id, Notification.user_id == user_id).first()
    if not n:
        return False
    n.is_read = True
    db.commit()
    return True


def mark_all_read(db: Session, user_id: int) -> int:
    count = db.query(Notification).filter(Notification.user_id == user_id, Notification.is_read == False).update({"is_read": True})
    db.commit()
    return count


def get_unread_count(db: Session, user_id: int) -> int:
    return db.query(Notification).filter(Notification.user_id == user_id, Notification.is_read == False).count()


def delete_notification(db: Session, notification_id: int, user_id: int) -> bool:
    n = db.query(Notification).filter(Notification.id == notification_id, Notification.user_id == user_id).first()
    if not n:
        return False
    db.delete(n)
    db.commit()
    return True
