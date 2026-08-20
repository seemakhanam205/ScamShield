from fastapi import HTTPException, status
from sqlalchemy.orm import Session 
from app.db.models import Entity, Report, ReportEntity
from app.schemas.report import ReportCreate 


def create_report(db:Session, report_data:ReportCreate, user_id:int)->Report:
    # 1. Create main report record 
    new_report=Report(
        user_id=user_id,
        report_type=report_data.report_type,
        description=report_data.description,
        amount=report_data.amount,
        transaction_id=report_data.transaction_id
    )
    db.add(new_report)
    db.commit()
    db.refresh(new_report)

    # 2. Process attached entites (PHONE, UPI, URL, EMAIL)
    for entity_in in report_data.entites:
        ent_type=entity_in.type.strip().upper()
        ent_value=entity_in.value.strip().lower()

        # Find existing entity or create a new one to keep values unique
        existing_entity=(
            db.query(Entity).filter(Entity.type==ent_type, Entity.value==ent_value).first() 
        )

        if not existing_entity:
            existing_entity=Entity(type=ent_type, value=ent_value)
            db.add(existing_entity)
            db.commit()
            db.refresh(existing_entity)

        # 3. Create junction link in report_entities 
        link=ReportEntity(
            report_id=new_report.id,
            entity_id=existing_entity.id
        )
        db.add(link)
        db.commit()
        db.refresh(new_report)

        return new_report
def get_user_reports(db:Session, user_id:int)->list[Report]:
    """ get me all the report entered by a user of id user_id"""
    return(
        db.query(Report).filter(Report.user_id==user_id).order_by(Report.created_at.desc()).all()
    )

def get_report_by_id(db:Session, report_id:int)->Report:
    """ Retrieves single report by id"""
    report = db.query(Report).filter(Report.id==report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Report not found"
        )
    return report