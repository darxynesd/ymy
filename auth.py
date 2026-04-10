from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from models import User
from database import SessionLocal

SECRET_KEY ="lala"
ALGORITHM= "HS256"
ACCESS_TOKEN_EXPIRE_MIN = 60*24

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_access_token(data:dict)->str:
    to_encode =data.copy()
    expire = datetime.utcnow()+ timedelta(minutes=ACCESS_TOKEN_EXPIRE_MIN)
    to_encode["exp"] = expire
    return jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        payload =jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None



oauth2_scheme=OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload =decode_token(token)

    if payload is None:
        raise HTTPException(401,"Токен nevalid")

    user_id =payload.get("user_id")
    if user_id is None:
        raise HTTPException(401,"token dont has user_id")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(401, "user not fonde")


    return user