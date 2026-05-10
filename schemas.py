from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict
from models import UserRole


class UserRegisterStep2(BaseModel):
    email: EmailStr
    username: str =Field(..., min_length=3, max_length=50)
    password: str =Field(..., min_length=8)
    confirm_password: str
    role: UserRole
    profile_name: Optional[str]=None
    profile_photo: Optional[str]= None


class UserRegisterStep3(BaseModel):
    user_id: int
    nickname: str = Field(..., min_length=3, max_length=50)
    avatar: Optional[str] =None#todo:заменить на загрузку файла
    banner: Optional[str]= None#todo:заменить на загрузку файла


class UserRegisterStep4(BaseModel):
    user_id: int
    phone: str
    profession_ids: List[int]
    tags: List[str]
    address: Optional[str] =None
    social_links: Optional[dict]=None


class ProfessionCreate(BaseModel):
    name: str


class ProfessionResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes=True


class TagResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes =True


class LoginRequest(BaseModel):
    login: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    role: str
    profile_name: Optional[str]=None
    master_id: Optional[int] =None