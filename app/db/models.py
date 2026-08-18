# structure of table for database
from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from app.db.database import Base

class Use(Base):
    __tablename__="users"

    id=Column(Integer, primary_key=True, index=True)
    email=Column(String, unique=True, nullable=False, index=True)
    password_hash=Column(String, nullable=False)
    full_name=Column(String, nullable=False)
    role=Column(String, default="USER",nullable=False)
    is_active=Column(Boolean, default=True,nullable=False)
    created_at=Column(DateTime, default=datetime.now(timezone.utc))