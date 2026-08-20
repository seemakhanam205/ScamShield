from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.schemas.report import ReportResponse
from typing import List
class EntitySearchResult(BaseModel):
    id:str
    type: str
    value:str
    report_count:int
    total_amount_lost:float
    risk_level:str # low, high , medium 
    created_at:datetime
    reports:List[ReportResponse]
