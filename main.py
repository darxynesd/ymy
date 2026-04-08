from database import engine, Base
from models import User
from fastapi import FastAPI
from database import SessionLocal
from fastapi import HTTPException

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return{"message": "Сервер работает "}



@app.post("/register")
def registor(username:str,password: str):
    db = SessionLocal()
    new_user= User(username=username, password=password )

    db.add(new_user)
    db.commit()


@app.post("/login")
def login(username: str, password:str):
    db = SessionLocal()

    user= db.query(User).filter(User.username == username).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if user.verify_password(password):
        return {"message": f"Привет, {username}!"}
    else:
        raise HTTPException(status_code=401, detail="Неверный пароль")    