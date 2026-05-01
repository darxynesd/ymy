from database import engine, Base
from fastapi import FastAPI, HTTPException, Depends
from database import SessionLocal
from fastapi import HTTPException
from schemas import (UserRegisterStep1, UserRegisterStep2,ProfessionCreate, ProfessionResponse,LoginRequest, LoginResponse)
from sqlalchemy.orm import Session
import json
from fastapi.middleware.cors import CORSMiddleware
from models import User, UserRole, Master, Profession
from auth import create_access_token, get_current_user

app = FastAPI(title="YMY")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

def get_db():
    db= SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "YMY. /docs"}

    #------------>Отсюда старт регистрации

@app.post("/register/step2")
def registor_step2(data: UserRegisterStep2,db: Session=Depends(get_db)):
    
    if db.query(User).filter(User.email== data.email).first():
        raise HTTPException(400, "Email уже зарегистрирован")

    if data.password != data.confirm_password:
        raise HTTPException(400,"Пароли не совпадают")

    if db.query(User).filter(User.username==data.username).first():
        raise HTTPException(400,"Username занят")

    user=User(email=data.email,
        username=data.username,
        password=data.password,
        role=data.role,
        profile_name=data.profile_name,
        profile_photo=data.profile_photo
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {
        "message": "Шаг 2 завершён",
        "user_id": user.id,
        "role": user.role.value
    }

@app.post("/register/step3")
def register_step3(data: UserRegisterStep3, db: Session =Depends(get_db)):

    user= db.query(User).filter(User.id== data.user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    if user.nickname:
        raise HTTPException(404, "Profield's been filed")

    user.nickname=  data.nickname
    user.avatar= data.avatar
    user.banner= data.banner

    dt.commit()
    db.refresh()

    if user.role ==UserRole.client:
        return{
            "message":"done",
            "user_id": new_user.id,
            "role":new_user.role.value
        }
    else:
        return {
            "message": "Шаг 3 завершён. Продолжите регистрацию мастера.",
            "user_id": user.id,
            "role":user.role.value,  
            "next_step": "/register/step4"
        }

@app.post("/register/step4")
def registor_step2(data: UserRegisterStep2, db: Session= Depends(get_db)):
    user=db.query(User).filter(User.id==data.user_id).first()
    if not user:
        raise HTTPException(404,"Пользователь не найден")
    if user.role !=UserRole.master:
        raise HTTPException(400, "Пользователь не является мастером")
    if user.master_profile:
        raise HTTPException(400, "Профиль мастера уже создан")    

    professions = db.query(Profession).filter(
        Profession.id.in_(data.profession_ids)
    ).all()
    if len(professions) !=len(data.profession_ids):
        raise HTTPException(400, "Некоторые профессии не найдены")
    
    tags=[]
    for tag_name in data.tags:
        tag_name=tag_name.lower().strip().lstrip("#")
        if not tag_name:
            continue

        tag= db,query(Tag).filter(tag.name== tag_name).first()
        if not tag:
            tag= Tag(name=tag_name)
            db.add(tag)
            db.flush()
        tags.append(tag)


    
    social_links_json =json.dumps(data.social_links) if data.social_links else None

    
    master = Master(
        user_id=data.user_id,
        phone=data.phone,
        address=data.address,
        social_links=social_links_json
    )
    master.professions=professions
    master.tags=tags
    
    db.add(master)
    db.commit()
    db.refresh(master)
    
    return {
        "message":"Регистрация мастера завершена!",
        "master_id": master.id,
        "professions": [p.name for p in professions],
        "tags": [t.name for t in tags]
    }


@app.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        (User.email == data.login) |  (User.username == data.login)).first()
    
    if not user or not user.verify_password(data.password):
        raise HTTPException(401, "Неверный логин или пароль")
    
    token= create_access_token({"user_id": user.id})

    response = {
        "access_token":token,
        "token_type": "bearer",
        "user_id":user.id,
        "role" : user.role.value,
        "profile_name":user.nickname
    }
    
    if user.role == UserRole.master and user.master_profile:
        response["master_id"] =user.master_profile.id
    
    return response

@app.get("/users/{user_id}")
def get_user_profile(user_id:int,db:Session =Depends(get_db), current_user: User= Depends(get_current_user)):
    user =db.query(User).filter(User.id==user_id).first()
    if current_user.id != user_id:
        raise HTTPException(403, "No access")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "Пользователь не найден")

    result ={
        "id": user.id,
        "email":user.email,
        "username":user.username,
        "role": user.role.value,
        "nickname": user.nickname,
        "avatar": user.avatar,
        "banner": user.banner
    }
    

    if user.role ==UserRole.master and user.master_profile:
        master= user.master_profile
        result["master"] = {
            "phone":master.phone,
            "address": master.address,
            "social_links":json.loads(master.social_links) if master.social_links else None,
            "rating":master.rating,
            "professions": [p.name for p in master.professions],
            "tags": [t.name for t in master.tags]
        }
    
    return result

@app.post("/professions", response_model=ProfessionResponse)

def create_profession(data: ProfessionCreate, db: Session= Depends(get_db)):
    if db.query(Profession).filter(Profession.name== data.name).first():
        raise HTTPException(400, "Profession exist")
        prof= Profession(name=data.name)
        db.add(prof)
        db.commit()
        db.refresh(prof)
        return prof

@app.get("/professions/",response_model=list[ProfessionResponse])
def get_professions(db:Session= Depends(get_db)):
    return db.query(Profession).all()

@app.get("/tags/", response_model=list[TagResponse])
def get_tags(db: Session = Depends(get_db)):
    return db.query(Tag).all()