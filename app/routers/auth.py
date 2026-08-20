from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
# OAuth2 expects: username and password
# So FastAPI gives us: from fastapi.security import OAuth2PasswordRequestForm
# This class already knows how to receive those two values.
from sqlalchemy.orm import Session 
from app.db.database import get_db
from app.schemas.user import Token, UserCreate, UserResponse
from app.services import auth_services
from app.core.dependencies import get_current_user
from app.db.models import User
router=APIRouter(prefix="/auth",tags=["Authentication"])
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data:UserCreate, db:Session=Depends(get_db)):
    return auth_services.register_user(db=db, user_data=user_data)

@router.post("/login",response_model=Token)
def login(form_data:OAuth2PasswordRequestForm=Depends(),
          db:Session=Depends(get_db)):
    return auth_services.authenticate_user(
        db=db,email=form_data.username, password=form_data.password
    ) # the email is username in this 

@router.get("/me",response_model=UserResponse)
def get_user_me(current_user:User=Depends(get_current_user)):
    return current_user