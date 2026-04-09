from database import engine, Base
from fastapi import FastAPI, HTTPException, Depends
from database import SessionLocal
from fastapi import HTTPException
from schemas import (UserRegisterStep1, UserRegisterStep2,ProfessionCreate, ProfessionResponse,LoginRequest, LoginResponse)
from sqlalchemy.orm import Session
import json
from models import User, UserRole, Master, Profession


app = FastAPI(title="YMY")

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

@app.post("/register/step1")
def registor_step1(data: UserRegisterStep1,db: Session=Depends(get_db)):
    
    if db.query(User).filter(User.email== data.email).first():
        raise HTTPException(400, "Email уже зарегистрирован")

    if db.query(User).filter(User.username==data.username).first():
        raise HTTPException(400, "Username занят")

    new_user=User(email=data.email,
    username=data.username,
    password=data.password,
    role=data.role,
    profile_name=data.profile_name,
    profile_photo=data.profile_photo
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    

    if data.role ==UserRole.client:
        return{
            "message":"done",
            "user_id": new_user.id,
            "role":new_user.role.value
        }
    else:
        return {
            "message": "Шаг 1 завершён. Продолжите регистрацию мастера.",
            "user_id": new_user.id,
            "role": new_user.role.value,  
            "next_step": "/register/step2"
        }

@app.post("/register/step2")
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
    if len(professions) != len(data.profession_ids):
        raise HTTPException(400, "Некоторые профессии не найдены")
    
   
    social_links_json =json.dumps(data.social_links) if data.social_links else None
    
    
    master = Master(
        user_id=data.user_id,
        phone=data.phone,
        address=data.address,
        social_links=social_links_json
    )
    master.professions=professions
    
    db.add(master)
    db.commit()
    db.refresh(master)
    
    return {
        "message":"Регистрация мастера завершена!",
        "master_id": master.id,
        "professions":[p.name for p in professions]
    }


@app.post("/professions",response_model=ProfessionResponse)
def create_profession(data:ProfessionCreate, db:Session = Depends(get_db)):
    existing =db.query(Profession).filter(Profession.name ==data.name).first()
    if existing:
        raise HTTPException(400, "Такая профессия уже есть")
    
    prof =Profession(name=data.name)
    db.add(prof)
    db.commit()
    db.refresh(prof)
    return prof
    
@app.get("/professions/",response_model= list[ProfessionResponse])
def get_professions(db:Session =Depends(get_db)):
    return db.query(Profession).all()





@app.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter((User.email == data.login) |  (User.username == data.login)).first()
    
    if not user or not user.verify_password(data.password):
        raise HTTPException(401, "Неверный логин или пароль")
    
    response = {
        "message": f"Привет, {user.profile_name}!",
        "user_id":user.id,
        "role" : user.role.value,
        "profile_name":user.profile_name
    }
    
    if user.role == UserRole.master and user.master_profile:
        response["master_id"] =user.master_profile.id
        response["address"]= user.master_profile.address
    
    return response

@app.get("/users/{user_id}")
def get_user_profile(user_id:int,db:Session =Depends(get_db)):
    user =db.query(User).filter(User.id==user_id).first()
    if not user:
        raise HTTPException(404, "Пользователь не найден")
    
    result ={
        "id": user.id,
        "email":user.email,
        "username":user.username,
        "role":user.role.value,
        "profile_name": user.profile_name,
        "profile_photo": user.profile_photo
    }
    

    if user.role ==UserRole.master and user.master_profile:
        master= user.master_profile
        result["master"] = {
            "phone":master.phone,
            "address": master.address,
            "social_links":json.loads(master.social_links) if master.social_links else None,
            "rating":master.rating,
            "professions":[p.name for p in master.professions]
        }
    
    return result