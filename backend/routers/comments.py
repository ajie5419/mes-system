from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from services import comment_service
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter(prefix="/api/v1/comments", tags=["评论系统"])


class CommentCreate(BaseModel):
    wo_id: Optional[int] = None
    resource_type: str  # work_order/milestone/exception/approval
    resource_id: int
    parent_id: Optional[int] = None
    content: str
    is_internal: Optional[bool] = False
    attachments: Optional[List] = None


@router.get("/")
def list_comments(db: Session = Depends(get_db), resource_type: str = None, resource_id: int = None, limit: int = 50):
    from models.comment import Comment
    q = db.query(Comment)
    if resource_type:
        q = q.filter(Comment.resource_type == resource_type)
    if resource_id:
        q = q.filter(Comment.resource_id == resource_id)
    return q.order_by(Comment.created_at.desc()).limit(limit).all()


@router.get("/{resource_type}/{resource_id}")
def list_comments(resource_type: str, resource_id: int, db: Session = Depends(get_db)):
    comments = comment_service.get_comments_by_resource(db, resource_type, resource_id)
    return comments


@router.post("/")
def create_comment(data: CommentCreate, db: Session = Depends(get_db)):
    # TODO: get user_id from auth
    user_id = 1
    comment = comment_service.create_comment(
        db, user_id=user_id,
        resource_type=data.resource_type, resource_id=data.resource_id,
        content=data.content, wo_id=data.wo_id, parent_id=data.parent_id,
        is_internal=data.is_internal, attachments=data.attachments,
    )
    return {"id": comment.id, "message": "评论发布成功"}


@router.delete("/{comment_id}")
def delete_comment(comment_id: int, db: Session = Depends(get_db)):
    # TODO: get user from auth
    is_admin = False
    user_id = 1
    if not comment_service.delete_comment(db, comment_id, user_id, is_admin):
        raise HTTPException(403, "无权删除此评论")
    return {"message": "评论已删除"}
