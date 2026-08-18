from fastapi import FastAPI
from sqlalchemy import text
from app.db.database import engine,Base
app=FastAPI()

Base.metadata.create_all(bind=engine)
@app.get("/")
def root():
    return {"message":"ScamShield API is running"}

