from datetime import datetime, timezone
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, default="USER", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    reports = relationship("Report", back_populates="user")


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    report_type = Column(String, nullable=False)  # SMS, EMAIL, PHONE, UPI, URL, TRANSACTION, OTHER
    description = Column(Text, nullable=False)
    amount = Column(Float, nullable=True)
    transaction_id = Column(String, nullable=True)
    status = Column(String, default="PENDING", nullable=False)  # PENDING, UNDER_REVIEW, VERIFIED, REJECTED
    risk_score = Column(Float, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user = relationship("User", back_populates="reports")
    entities = relationship("ReportEntity", back_populates="report")


class Campaign(Base):
    """Groups connected entities (Phone, UPI, URL) into flagged network clusters."""
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    risk_score = Column(Float, default=0.0)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    entities = relationship("Entity", back_populates="campaign")


class Entity(Base):
    __tablename__ = "entities"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False, index=True)  # PHONE, UPI, URL, EMAIL
    value = Column(String, nullable=False, index=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Foreign key to associate an entity with a Scam Campaign
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)

    # Relationships
    campaign = relationship("Campaign", back_populates="entities")
    reports = relationship("ReportEntity", back_populates="entity")

    __table_args__ = (
        UniqueConstraint("type", "value", name="uq_entity_type_value"),
    )


class ReportEntity(Base):
    __tablename__ = "report_entities"

    report_id = Column(Integer, ForeignKey("reports.id"), primary_key=True)
    entity_id = Column(Integer, ForeignKey("entities.id"), primary_key=True)

    report = relationship("Report", back_populates="entities")
    entity = relationship("Entity", back_populates="reports")