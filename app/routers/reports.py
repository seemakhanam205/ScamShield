from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.db.models import User
from app.schemas.report import ReportCreate, ReportResponse
from app.services import report_services

reports_router=APIRouter(prefix="/reports",tags=["Reports"])


@reports_router.post("/new",response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def create_new_report(
    report_data:ReportCreate,
    db:Session=Depends(get_db),
    current_user:User=Depends(get_current_user)
):
    """Submits a new scam report attached to the current user."""
    return report_services.create_report(
        db=db, report_data=report_data, user_id=current_user.id
    )

@reports_router.get("/me", response_model=list[ReportResponse])
def get_my_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fetches all scam reports submitted by the logged-in user."""
    return report_services.get_user_reports(db=db, user_id=current_user.id)


@reports_router.get("/{report_id}", response_model=ReportResponse)
def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fetches details of a specific report by ID."""
    return report_services.get_report_by_id(db=db, report_id=report_id)