# structure of table for database
from datetime import datetime, timezone
from sqlalchemy import (Boolean, Column, DateTime, Integer, String, Text, Float,ForeignKey)
from app.db.database import Base
from sqlalchemy.orm import relationship
class User(Base):
    __tablename__="users"

    id=Column(Integer, primary_key=True, index=True)
    email=Column(String, unique=True, nullable=False, index=True)
    password_hash=Column(String, nullable=False)
    full_name=Column(String, nullable=False)
    role=Column(String, default="USER",nullable=False)
    is_active=Column(Boolean, default=True,nullable=False)
    created_at=Column(DateTime, default=datetime.now())
    reports = relationship("Report", back_populates="user")  #this back_populates is for one-> many relationship (one user-> many reports)

class Report(Base):
    __tablename__="reports"
    id=Column(Integer, primary_key=True, index=True)
    user_id=Column(Integer, ForeignKey("users.id"), nullable=False)
    report_type=Column(String, nullable=False) #SMS, EMAIL, PHONE, UPI, URL, TRANSACTION, OTHER
    description=Column(Text, nullable=False)
    amount=Column(Float, nullable=True)
    transaction_id=Column(String, nullable=True)
    status=Column(String, default="PENDING",nullable=False) # PENDING UNDER_REVIEW VERIFIED REJECTED
    risk_score=Column(Float, nullable=True)
    created_at=Column(DateTime(timezone=True),
                      default=lambda:datetime.now(timezone.utc),
                      nullable=False,)
    updated_at=Column(
        DateTime(timezone=True),
        default=lambda:datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    user = relationship("User", back_populates="reports")
    entities = relationship("ReportEntity", back_populates="report")

class Entity(Base):
    #Uniqueness: Each identifier exists only once in this table. If 100 people report the same phone number, the phone number is stored once in entities.
    __tablename__= "entities"
    id=Column(Integer,primary_key=True, index=True)
    type=Column(String, nullable=False, index=True) # PHONE, UPI, URL, EMAIL
    value=Column(String, nullable=False, index=True)
    created_at=Column(
        DateTime(timezone=True),
        default=lambda:datetime.now(timezone.utc),
        nullable=False
    )
    reports = relationship("ReportEntity", back_populates="entity")

class ReportEntity(Base):
    __tablename__ = "report_entities"
    #Connects reports to entities in a Many-to-Many (N:M) relationship.
    report_id = Column(Integer, ForeignKey("reports.id"), primary_key=True)
    entity_id = Column(Integer, ForeignKey("entities.id"), primary_key=True)

    # Relationships
    report = relationship("Report", back_populates="entities")
    entity = relationship("Entity", back_populates="reports")