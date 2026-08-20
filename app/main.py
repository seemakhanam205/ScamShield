from fastapi import FastAPI
from sqlalchemy import text
from app.routers.auth import auth_router 
import app.db.models 
from app.routers.admin import admin_router
from app.routers.search import search_router
from app.routers.reports import reports_router
from app.db.database import engine,Base
app=FastAPI(title="ScamShield API", version="1.0.0")
app.include_router(auth_router)
app.include_router(search_router)
app.include_router(reports_router)
app.include_router(admin_router)
Base.metadata.create_all(bind=engine)
@app.get("/")
def root():
    return {"message":"ScamShield API is running"}

