from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone 
from pwdlib.hashers.bcrypt import BcryptHasher
import jwt 
from app.core.config import settings

password_hash=PasswordHash.recommended()


def hash_password(password:str)-> str:
    return password_hash.hash(password)

def verify_password(password:str,password_hash:str)->bool:
    return password_hash.verify(password,password_hash)

def create_access_token(data:dict, expires_delta:timedelta|None=None)->str:
    """Generating a signed JWT token """
    to_encode=data.copy()
    expire=datetime.now(timezone.utc)+(
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTE)
    )
    to_encode.update({"exp":expire})
    return jwt.encode(to_encode,settings.SECRET_KEY,algorithm=settings.ALGORIHTM)