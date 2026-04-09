from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    wo_id = Column(Integer, ForeignKey("work_orders.id"), nullable=True, index=True)
    resource_type = Column(String(50), nullable=False, index=True,
                           comment="work_order/milestone/exception/approval")
    resource_id = Column(Integer, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True, index=True)
    content = Column(Text, nullable=False)
    mentions = Column(JSON, nullable=True, default=list, comment="@提及的用户ID列表")
    attachments = Column(JSON, nullable=True, default=list, comment="附件ID列表")
    is_internal = Column(Boolean, default=False, comment="内部备注仅同部门可见")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    user = relationship("User")
    parent = relationship("Comment", remote_side=[id])
    replies = relationship("Comment", backref="parent_comment", remote_side=[parent_id],
                           lazy="dynamic", order_by="Comment.created_at")
