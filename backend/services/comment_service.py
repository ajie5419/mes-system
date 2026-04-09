import re
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from models.comment import Comment
from models.user import User
from datetime import datetime

logger = logging.getLogger(__name__)


def get_mentions(content: str) -> List[int]:
    """解析 @提及，返回用户ID列表。支持 @用户名 格式"""
    pattern = r'@(\w+)'
    matches = re.findall(pattern, content)
    if not matches:
        return []
    return []  # 实际解析需要查数据库，返回匹配到的用户名列表由调用方处理


def create_comment(db: Session, user_id: int, resource_type: str, resource_id: int,
                   content: str, wo_id: int = None, parent_id: int = None,
                   is_internal: bool = False, attachments: list = None) -> Comment:
    # Parse mentions
    mention_names = re.findall(r'@(\w+)', content)
    mentioned_ids = []
    if mention_names:
        users = db.query(User).filter(User.username.in_(mention_names)).all()
        mentioned_ids = [u.id for u in users]

    comment = Comment(
        wo_id=wo_id, resource_type=resource_type, resource_id=resource_id,
        user_id=user_id, parent_id=parent_id, content=content,
        mentions=mentioned_ids, attachments=attachments or [],
        is_internal=is_internal,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    # Notify mentioned users
    if mentioned_ids:
        try:
            from services.notification_service import create_notification
            user = db.query(User).get(user_id)
            username = user.display_name if user else "unknown"
            for uid in mentioned_ids:
                if uid != user_id:
                    create_notification(
                        db, uid,
                        title=f"{username} 提及了你",
                        content=content[:100],
                        type="info",
                        resource_type=resource_type,
                        resource_id=resource_id,
                    )
        except Exception as e:
            logger.error(f"通知提及用户失败: {e}")

    return comment


def get_comments_by_resource(db: Session, resource_type: str, resource_id: int,
                              user_id: int = None) -> List[dict]:
    """获取某资源的评论列表（树形结构）"""
    query = db.query(Comment).filter(
        Comment.resource_type == resource_type,
        Comment.resource_id == resource_id,
        Comment.parent_id == None,
    ).order_by(Comment.created_at.desc()).all()

    result = []
    for c in query:
        # Filter internal comments
        if c.is_internal and user_id:
            comment_user = db.query(User).get(c.user_id)
            if not comment_user or comment_user.department != (db.query(User).get(user_id).department if db.query(User).get(user_id) else None):
                continue

        item = _comment_to_dict(c)
        # Load replies
        replies = db.query(Comment).filter(Comment.parent_id == c.id).order_by(Comment.created_at.asc()).all()
        item["replies"] = [_comment_to_dict(r) for r in replies]
        result.append(item)

    return result


def get_comments(db: Session, wo_id: int = None, resource_type: str = None,
                 resource_id: int = None) -> List[Comment]:
    q = db.query(Comment)
    if wo_id:
        q = q.filter(Comment.wo_id == wo_id)
    if resource_type:
        q = q.filter(Comment.resource_type == resource_type)
    if resource_id:
        q = q.filter(Comment.resource_id == resource_id)
    return q.order_by(Comment.created_at.desc()).all()


def delete_comment(db: Session, comment_id: int, user_id: int, is_admin: bool = False) -> bool:
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        return False
    if comment.user_id != user_id and not is_admin:
        return False
    # Delete replies first
    replies = db.query(Comment).filter(Comment.parent_id == comment_id).all()
    for r in replies:
        db.delete(r)
    db.delete(comment)
    db.commit()
    return True


def _comment_to_dict(c: Comment) -> dict:
    user = None
    try:
        from sqlalchemy.orm import object_session
        s = object_session(c)
        if s:
            user = s.query(User).get(c.user_id)
    except:
        pass
    return {
        "id": c.id,
        "content": c.content,
        "user_id": c.user_id,
        "username": user.display_name if user else "未知",
        "user_department": user.department if user else "",
        "parent_id": c.parent_id,
        "mentions": c.mentions or [],
        "attachments": c.attachments or [],
        "is_internal": c.is_internal,
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "replies": [],
    }
