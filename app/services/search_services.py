from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.db.models import Entity, Report, ReportEntity


def search_entity(db: Session, query_type: str, query_value: str) -> dict:
    # Normalize inputs
    q_type = query_type.strip().upper()
    q_value = query_value.strip().lower()

    # Query entity
    entity = (
        db.query(Entity)
        .filter(Entity.type == q_type, Entity.value == q_value)
        .first()
    )

    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No scam reports found for {q_type}: '{q_value}'",
        )

    # Fetch linked reports via junction table
    reports = (
        db.query(Report)
        .join(ReportEntity, Report.id == ReportEntity.report_id)
        .filter(ReportEntity.entity_id == entity.id)
        .all()
    )

    report_count = len(reports)

    # Calculate total money lost through this entity
    total_amount_lost = sum(r.amount for r in reports if r.amount is not None)

    # Determine risk level based on report count
    if report_count >= 5:
        risk_level = "HIGH"
    elif report_count >= 2:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "id": entity.id,
        "type": entity.type,
        "value": entity.value,
        "report_count": report_count,
        "total_amount_lost": total_amount_lost,
        "risk_level": risk_level,
        "created_at": entity.created_at,
        "reports": reports,
    }