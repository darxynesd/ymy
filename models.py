from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table, Enum as SQLEnum
from database import Base
from passlib.context import CryptContext
import enum
from sqlalchemy.orm import relationship

pwd_context=CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRole(str, enum.Enum):
    client= "client"
    master="master"

master_professions=Table(
    "master_professions",
    Base.metadata,
    Column("master_id",Integer,ForeignKey("masters.id")),
    Column("profession_id", Integer, ForeignKey("professions.id"))
)

master_tags =Table(
    "master_tags",
    Base.metadata,
    Column("master_id",Integer, ForeignKey("masters.id")),
    Column("tag_id", Integer,ForeignKey("tags.id"))
)



class User(Base):
    __tablename__ ="users"

    id =Column(Integer,primary_key=True, index=True)
    email =Column(String, unique=True,index=True, nullable=False)
    username= Column(String,unique=True, index=True,  nullable=False)
    hashed_password =Column(String, nullable=False)
    role = Column(SQLEnum(UserRole),  nullable=False,default=UserRole.client)

    nickname =Column(String, nullable =True)
    avatar=Column(String,nullable=True)
    banner=Column(String,nullable=True)

    master_profile = relationship("Master", back_populates="user", uselist=False)

    def __init__(self,email, username,password,role,nickname=None,avatar=None, banner=None):
        self.email = email.lower().strip()
        self.username=username
        self.hashed_password= pwd_context.hash(password)
        self.role=role
        self.nickname =nickname
        self.avatar =avatar
        self.banner= banner

    def verify_password(self, plain_password: str) -> bool:
        return pwd_context.verify(plain_password,self.hashed_password)



class Master(Base):
    __tablename__ ="masters"

    id =Column(Integer,primary_key=True,index=True, nullable=False)
    user_id =Column(Integer,ForeignKey("users.id"),unique=True)

    phone =Column(String,nullable=True)
    social_links=Column(String, nullable=True)
    address =Column(String, nullable=True)#todo добавить latitude,longitude для карты

    rating=Column(Integer,default=0)#todo переделать integer и логику рейтинга. пока пусть стоит так
    is_active= Column(Boolean, default=True)

    user = relationship("User", back_populates="master_profile")
    professions=relationship("Profession",secondary=master_professions, back_populates="masters")
    tags=relationship("Tag",secondary=master_tags, back_populates="masters")



class Profession(Base):
    __tablename__="professions"

    id =Column(Integer, primary_key=True, index=True)
    name=Column(String, unique=True, nullable=False)

    masters =relationship("Master",secondary=master_professions, back_populates="professions")



class Tag(Base):
    __tablename__="tags"

    id =Column(Integer,primary_key=True, index=True)
    name= Column(String,unique=True,nullable=False)

    masters=relationship("Master", secondary=master_tags,back_populates="tags")