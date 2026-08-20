from datetime import datetime
from pydantic import BaseModel, ConfigDict


# Schema for submitting an attached entity (Phone, UPI, URL, Email)
class EntityCreate(BaseModel):
    type: str  # PHONE, UPI, URL, EMAIL
    value: str


# Schema for returning entity data in responses
class EntityResponse(BaseModel):
    id: int
    type: str
    value: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Schema for incoming report creation requests
class ReportCreate(BaseModel):
    report_type: str  # SMS, EMAIL, PHONE, UPI, URL, TRANSACTION, OTHER
    description: str
    amount: float | None = None
    transaction_id: str | None = None
    entities: list[EntityCreate] = []  # List of attached scam entities


# Schema for returning report data
class ReportResponse(BaseModel):
    id: int
    user_id: int
    report_type: str
    description: str
    amount: float | None = None
    transaction_id: str | None = None
    status: str
    risk_score: float | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)