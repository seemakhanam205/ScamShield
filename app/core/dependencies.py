from fastapi import Depends, HTTPException, status 
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import PyJWTError
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
def get_current_user(token:str=Depends(oauth2_scheme),db:Session=Depends(get_db))->User:
    cred_exception=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="could not validate credentials")
    try:
        payload=jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id:str| None =payload.get("sub")
        if user_id is None:
            raise cred_exception
    except PyJWTError:
        raise cred_exception
    user=db.query(User).filter(User.id==int(user_id)).first()
    if user is None:
        raise cred_exception
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Inactive user account")
    return user

