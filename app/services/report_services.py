import re
import joblib

from typing import List, Tuple, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models import Entity, Report, ReportEntity, Campaign
from app.schemas.report import ReportCreate


# ==============================================================================
# REGEX PATTERNS
# ==============================================================================

PHONE_REGEX = r"\b(?:\+?91[-\s]?)?[6-9]\d{9}\b"

# Basic UPI ID pattern.
# This is intentionally kept separate from email detection.
UPI_REGEX = r"\b[a-zA-Z0-9._-]+@[a-zA-Z]{2,}\b"

URL_REGEX = (
    r"https?://\S+"
    r"|www\.\S+"
    r"|\b[\w.-]+\.(?:xyz|online|site|tech|apk|in|com|org|net)\b"
)


# ==============================================================================
# ML MODEL
# ==============================================================================

MODEL_PATH = "scamshield_model.joblib"
VECTORIZER_PATH = "scamshield_vectorizer.joblib"

model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)


# ==============================================================================
# ML PREDICTION
# ==============================================================================

def predict_text_scam_probability(text: str) -> float:
    """
    Predict scam probability using:
        TF-IDF + Logistic Regression

    Returns:
        Scam probability as a percentage between 0 and 100.
    """

    vec = vectorizer.transform([text])

    scam_probability = model.predict_proba(vec)[0][1] * 100

    return round(float(scam_probability), 2)


# ==============================================================================
# ENTITY EXTRACTION
# ==============================================================================

def extract_entities_from_text(
    text: str,
) -> List[Tuple[str, str]]:
    """
    Extract unique entities from report description.

    Supported entities:
        URL
        PHONE
        UPI
    """

    entities = set()

    # --------------------------------------------------------------------------
    # URLs
    # --------------------------------------------------------------------------

    for url in re.findall(URL_REGEX, text, re.IGNORECASE):
        # Remove common punctuation accidentally captured at the end
        cleaned_url = url.rstrip(".,!?;:)")

        entities.add(
            ("URL", cleaned_url.lower())
        )

    # --------------------------------------------------------------------------
    # Phone numbers
    # --------------------------------------------------------------------------

    for phone in re.findall(PHONE_REGEX, text):
        entities.add(
            ("PHONE", phone.strip())
        )

    # --------------------------------------------------------------------------
    # UPI IDs
    # --------------------------------------------------------------------------

    for upi in re.findall(UPI_REGEX, text, re.IGNORECASE):
        upi = upi.lower()

        # Avoid treating normal email addresses as UPI IDs.
        # This is still a heuristic because UPI IDs and emails
        # have similar syntax.
        if not upi.endswith(
            (
                "@gmail.com",
                "@yahoo.com",
                "@outlook.com",
                "@hotmail.com",
                "@icloud.com",
            )
        ):
            entities.add(
                ("UPI", upi)
            )

    return list(entities)


# ==============================================================================
# ENTITY DATABASE HELPER
# ==============================================================================

def get_or_create_entity(
    db: Session,
    entity_type: str,
    entity_value: str,
) -> Entity:
    """
    Find an existing entity or create a new one.
    """

    entity_type = entity_type.strip().upper()
    entity_value = entity_value.strip().lower()

    existing_entity = (
        db.query(Entity)
        .filter(
            Entity.type == entity_type,
            Entity.value == entity_value,
        )
        .first()
    )

    if existing_entity:
        return existing_entity

    new_entity = Entity(
        type=entity_type,
        value=entity_value,
    )

    db.add(new_entity)

    # Flush so that new_entity.id becomes available
    # before creating ReportEntity.
    db.flush()

    return new_entity


# ==============================================================================
# REPORT CREATION
# ==============================================================================

def create_report(
    db: Session,
    report_data: ReportCreate,
    user_id: int,
) -> Report:
    """
    Create a scam report.

    Workflow:

    1. Run ML model on report description.
    2. Calculate scam risk score.
    3. Create Report record.
    4. Extract PHONE / UPI / URL entities from description.
    5. Create or reuse entities in database.
    6. Link entities to report.
    7. Connect entities to existing campaigns.
    8. Create a new campaign if necessary.
    9. Commit everything once.
    """

    try:

        # ======================================================================
        # 1. ML PREDICTION
        # ======================================================================

        scam_risk_score = predict_text_scam_probability(
            report_data.description
        )

        # ======================================================================
        # 2. CREATE REPORT
        # ======================================================================

        new_report = Report(
            user_id=user_id,
            report_type=report_data.report_type,
            description=report_data.description,
            amount=report_data.amount,
            transaction_id=report_data.transaction_id,
            risk_score=scam_risk_score,
            status=(
                "UNDER_REVIEW"
                if scam_risk_score > 50
                else "PENDING"
            ),
        )

        db.add(new_report)

        # We need report.id before creating ReportEntity records.
        db.flush()

        # ======================================================================
        # 3. EXTRACT ENTITIES FROM DESCRIPTION
        # ======================================================================

        extracted_entities = extract_entities_from_text(
            report_data.description
        )

        # Store database entities here.
        db_entities: List[Entity] = []

        # Keep track of campaigns already associated
        # with extracted entities.
        connected_campaign_ids = set()

        # ======================================================================
        # 4. CREATE / REUSE ENTITIES
        # ======================================================================

        for entity_type, entity_value in extracted_entities:

            entity = get_or_create_entity(
                db=db,
                entity_type=entity_type,
                entity_value=entity_value,
            )

            db_entities.append(entity)

            # --------------------------------------------------------------
            # Existing campaign?
            # --------------------------------------------------------------

            if entity.campaign_id is not None:
                connected_campaign_ids.add(
                    entity.campaign_id
                )

            # --------------------------------------------------------------
            # Link report ↔ entity
            # --------------------------------------------------------------

            existing_link = (
                db.query(ReportEntity)
                .filter(
                    ReportEntity.report_id == new_report.id,
                    ReportEntity.entity_id == entity.id,
                )
                .first()
            )

            if not existing_link:

                link = ReportEntity(
                    report_id=new_report.id,
                    entity_id=entity.id,
                )

                db.add(link)

        # ======================================================================
        # 5. CAMPAIGN HANDLING
        # ======================================================================

        target_campaign: Optional[Campaign] = None

        # ----------------------------------------------------------------------
        # Case 1:
        # All extracted entities already belong to exactly one campaign.
        # ----------------------------------------------------------------------

        if len(connected_campaign_ids) == 1:

            campaign_id = next(
                iter(connected_campaign_ids)
            )

            target_campaign = (
                db.query(Campaign)
                .filter(
                    Campaign.id == campaign_id
                )
                .first()
            )

        # ----------------------------------------------------------------------
        # Case 2:
        # Entities belong to multiple campaigns.
        #
        # We merge them into the first campaign.
        # ----------------------------------------------------------------------

        elif len(connected_campaign_ids) > 1:

            campaign_ids = list(
                connected_campaign_ids
            )

            primary_campaign_id = campaign_ids[0]

            target_campaign = (
                db.query(Campaign)
                .filter(
                    Campaign.id == primary_campaign_id
                )
                .first()
            )

            if target_campaign:

                other_campaign_ids = campaign_ids[1:]

                (
                    db.query(Entity)
                    .filter(
                        Entity.campaign_id.in_(
                            other_campaign_ids
                        )
                    )
                    .update(
                        {
                            Entity.campaign_id:
                                target_campaign.id
                        },
                        synchronize_session=False,
                    )
                )

        # ----------------------------------------------------------------------
        # Case 3:
        # No existing campaign, but at least two entities were found.
        #
        # Create a new campaign.
        # ----------------------------------------------------------------------

        elif len(db_entities) >= 2:

            first_entity = db_entities[0]

            campaign_name = (
                f"Campaign-"
                f"{first_entity.type}-"
                f"{first_entity.value[:8]}"
            )

            target_campaign = Campaign(
                name=campaign_name,
                risk_score=scam_risk_score,
            )

            db.add(target_campaign)

            db.flush()

        # ======================================================================
        # 6. ASSIGN CAMPAIGN TO ENTITIES
        # ======================================================================

        if target_campaign:

            for entity in db_entities:

                entity.campaign_id = target_campaign.id

        # ======================================================================
        # 7. COMMIT EVERYTHING
        # ======================================================================

        db.commit()

        # Refresh report with database-generated values.
        db.refresh(new_report)

        return new_report

    except Exception:

        # Roll back everything if any database operation fails.
        db.rollback()

        raise


# ==============================================================================
# GET ALL REPORTS FOR A USER
# ==============================================================================

def get_user_reports(
    db: Session,
    user_id: int,
) -> List[Report]:
    """
    Get all reports submitted by a specific user.
    """

    return (
        db.query(Report)
        .filter(
            Report.user_id == user_id
        )
        .order_by(
            Report.created_at.desc()
        )
        .all()
    )


# ==============================================================================
# GET SINGLE REPORT
# ==============================================================================

def get_report_by_id(
    db: Session,
    report_id: int,
) -> Report:
    """
    Retrieve a single report by ID.
    """

    report = (
        db.query(Report)
        .filter(
            Report.id == report_id
        )
        .first()
    )

    if not report:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )

    return report