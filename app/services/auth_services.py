from fastapi import HTTPException, status 
from sqlalchemy.orm import Session 
from app.core.security import create_access_token, hash_password, verify_password
from app.db.models import User
from app.schemas.user import Token, UserCreate
from app.db.database import get_db

def register_user(db:Session, user_data:UserCreate)-> User:
    # check if user with given email already exits 
    existing_user=db.query(User).filter(User.email==user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Email already registered")
    hashed_pwd=hash_password(user_data.password)
    db_user=User(
        full_name=user_data.full_name,
        email=user_data.email,
        password_hash=hashed_pwd
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db:Session, email:str, password:str)->Token:
    user=db.query(User).filter(User.email==email).first()
    if not user or verify_password(password,user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN
        )
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
    return Token(access_token=access_token, token_type="bearer")