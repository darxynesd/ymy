from pydantic import BaseModel, EmailStr, Field
from typing import List,Optional, Dict
from models import UserRole

class UserRegisterStep1(BaseModel):
    email: EmailStr
    username:str=Field(...,min_length=3,max_length=50)
    password: str= Field(...,min_length=8)
    role: UserRole
    profile_name: str= Field(..., min_length=3, max_length=50)
    profile_photo: Optional[str]=None#конченый бред .надо переделать

class UserRegisterStep2(BaseModel):
    user_id:int
    phone  :str
    address:str
    social_links:dict
    profession_ids: List[int]
    profile_photo:Optional[str]

class ProfessionCreate(BaseModel):
    name: str

class ProfessionResponse(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True

class userResponse(BaseModel):
    id: int
    email: str
    username: str
    role: UserRole
    social_links: Optional[str]
    rating:int
    profassions: List[ProfessionResponse]

    class Config:
        from_attributes=True 

class LoginRequest(BaseModel):
    login:str
    password:str

class LoginResponse(BaseModel):
    message:str
    user_id:int
    role: UserRole
    profile_name:str
    master_id:Optional[int] =None 
    address: Optional[str]=None