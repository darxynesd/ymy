from sqlalchemy import Column, Integer,String
from database import Base
from passlib.context import CryptContext


pwd_context= CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    __tablename__="users"
    #колонки
    id = Column(Integer,primary_key=True,index=True)
    username=Column(String, unique=True, index=True)
    hashed_password=Column(String)

    def __init__(self, username:str, password:str):
        self.username = username
        self.hashed_password = pwd_context.hash(password)

    def verify_password(self, plain_password:str) -> bool:
        return pwd_context.verify(plain_password, self.hashed_password)