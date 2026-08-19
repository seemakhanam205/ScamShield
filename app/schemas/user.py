from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime

class UserCreate(BaseModel):
    full_name:str
    email:str
    password:str

class UserResponse(BaseModel):
    id:int
    email:str
    full_name:str
    role:str
    is_active:bool
    created_at:datetime
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token:str
    token_types:str="bearer"