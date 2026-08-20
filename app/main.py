from fastapi import FastAPI
from sqlalchemy import text
from app.routers.auth import auth_router 
import app.db.models 
from app.routers.search import router
from app.routers.reports import report_router
from app.db.database import engine,Base
app=FastAPI(title="ScamShield API", version="1.0.0")
app.include_router(auth_router)
app.include_router(report_router)
app.include_router(router)
Base.metadata.create_all(bind=engine)
@app.get("/")
def root():
    return {"message":"ScamShield API is running"}

