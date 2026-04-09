from sqlalchemy.orm import Session
from models.user import User
from schemas.user import UserCreate, UserUpdate
from typing import List, Optional

def create_user(db: Session, data: UserCreate) -> User:
    """招纳新修行者"""
    db_user = User(
        username=data.username,
        display_name=data.display_name,
        department=data.department.value,
        role=data.role.value,
        hashed_password="placeholder-password" # 暂不实现复杂加密
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users(db: Session, department: Optional[str] = None) -> List[User]:
    """查阅名册"""
    query = db.query(User)
    if department:
        query = query.filter(User.department == department)
    return query.all()

def update_user(db: Session, user_id: int, data: UserUpdate) -> Optional[User]:
    """调动职守"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return None
    
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if hasattr(db_user, key):
            # 处理枚举类型
            setattr(db_user, key, value.value if hasattr(value, 'value') else value)
    
    db.commit()
    db.refresh(db_user)
    return db_user
