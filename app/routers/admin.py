from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.db.models import Report, User
from app.schemas.report import ReportResponse

admin_router = APIRouter(prefix="/admin", tags=["Admin Operations"])


class ReportStatusUpdate(BaseModel):
    status: str  # e.g., "PENDING", "VERIFIED", "REJECTED", "RESOLVED"
    risk_score: float | None = None


# Dependency to ensure only ADMIN users can access these routes
def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user


@admin_router.get("/reports", response_model=list[ReportResponse])
def get_all_reports_for_admin(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Retrieves all reports in the system for admin review."""
    return db.query(Report).order_by(Report.created_at.desc()).all()


@admin_router.patch("/reports/{report_id}", response_model=ReportResponse)
def update_report_status(
    report_id: int,
    update_data: ReportStatusUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Updates the moderation status and risk score of a report."""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Report not found"
        )

    report.status = update_data.status
    if update_data.risk_score is not None:
        report.risk_score = update_data.risk_score

    db.commit()
    db.refresh(report)
    return report