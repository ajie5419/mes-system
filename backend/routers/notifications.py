from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from services import auth_service
from services.notification_service import get_user_notifications, mark_as_read, mark_all_read, get_unread_count, delete_notification

router = APIRouter(prefix="/api/v1/notifications", tags=["通知"])


@router.get("")
def list_notifications(
    unread_only: bool = Query(False),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(auth_service.get_current_user),
):
    total, items = get_user_notifications(db, current_user.id, unread_only, page, page_size)
    return {"total": total, "items": [{"id": n.id, "title": n.title, "content": n.content, "type": n.type, "is_read": n.is_read, "related_resource_type": n.related_resource_type, "related_resource_id": n.related_resource_id, "created_at": n.created_at.isoformat() if n.created_at else None} for n in items]}


@router.get("/unread-count")
def unread_count(
    db: Session = Depends(get_db),
    current_user=Depends(auth_service.get_current_user),
):
    return {"count": get_unread_count(db, current_user.id)}


@router.put("/{notification_id}/read")
def read_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth_service.get_current_user),
):
    if not mark_as_read(db, notification_id, current_user.id):
        raise HTTPException(404, "通知不存在")
    return {"message": "已标记为已读"}


@router.put("/read-all")
def read_all(
    db: Session = Depends(get_db),
    current_user=Depends(auth_service.get_current_user),
):
    count = mark_all_read(db, current_user.id)
    return {"message": f"已标记 {count} 条为已读"}


@router.delete("/{notification_id}")
def remove_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth_service.get_current_user),
):
    if not delete_notification(db, notification_id, current_user.id):
        raise HTTPException(404, "通知不存在")
    return {"message": "已删除"}
