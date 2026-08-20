from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.search import EntitySearchResult
from app.services import search_services

search_router = APIRouter(prefix="/search", tags=["Search & Lookup"])


@search_router.get("/", response_model=EntitySearchResult)
def search(
    type: str = Query(..., description="Entity type: PHONE, UPI, URL, EMAIL"),
    value: str = Query(..., description="The value to check, e.g., 'scammer123@upi'"),
    db: Session = Depends(get_db),
):
    """Searches for a scam entity (Phone, UPI, URL, Email) and retrieves its risk profile and linked reports."""
    return search_services.search_entity(db=db, query_type=type, query_value=value)