from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from database import Base


class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token_jti = Column(String(100), unique=True, nullable=False, index=True)
    revoked_at = Column(DateTime, default=datetime.now)
