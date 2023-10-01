from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from hugchat import hugchat
from hugchat.login import Login
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from passlib.hash import bcrypt
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import csv
import tempfile
import os
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "https://x.thunkable.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.environ.get('postgres://JiyelL:X6Iuq1bgQySs@ep-plain-flower-54000100.ap-southeast-1.aws.neon.tech/neondb')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    user_id = Column(String, unique=True, index=True)

class SoilData(Base):
    __tablename__ = "soil_data"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    date_time = Column(String, index=True)
    soil_name = Column(String, index=True)
    nitrogen = Column(Float)
    phosphorus = Column(Float)
    potassium = Column(Float)
    moisture = Column(Integer)
    temperature = Column(Float)

class SoilRecommends(Base):
    __tablename__ = "soil_recommends"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    date_time = Column(String, index=True)
    soil_name = Column(String, index=True)
    crop_name = Column(String, index=True)
    soil_area = Column(Float)
    nitrogen = Column(Float)
    phosphorus = Column(Float)
    potassium = Column(Float)
    recommendations = Column(String)
    
class UserBase(BaseModel):
    username: str
    password: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    user_id: str

    class Config:
        orm_mode = True

class SoilDataBase(BaseModel):
    user_id: str
    date_time: str
    soil_name: str
    nitrogen: float
    phosphorus: float
    potassium: float
    moisture: int
    temperature: float

class SoilDataCreate(SoilDataBase):
    pass

class SoilData(SoilDataBase):
    id: int

    class Config:
        orm_mode = True

class SoilRecommendsBase(BaseModel):
    user_id: str
    date_time: str
    soil_name: str
    crop_name: str
    soil_area: float
    nitrogen: float
    phosphorus: float
    potassium: float
    recommendations: str

class SoilRecommendsCreate(SoilRecommendsBase):
    pass

class SoilRecommends(SoilRecommendsBase):
    id: int

    class Config:
        orm_mode = True
    
class Message(BaseModel):
    message: str

# Log in to huggingface and grant authorization to huggingchat
sign = Login("gsarmiento0798@gmail.com", "Blankshounen_30")
cookies = sign.login()

# Create a temporary directory to store cookies
with tempfile.TemporaryDirectory() as temp_dir:
    cookie_path = os.path.join(temp_dir, "cookies.json")
    sign.saveCookiesToDir(cookie_path)

# Create a ChatBot
chatbot = hugchat.ChatBot(cookies=cookies.get_dict())


@app.put("/message")
async def update_message(message: Message):

    # Get a response from the chatbot
    response = chatbot.chat(message.message)

    return {"response": response}

# Define your endpoints
@app.post("/users/", response_model=User)
async def create_user(user: UserCreate):
    db = SessionLocal()
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="existing username error")
    else:
        user = User(**user.dict())
        user.user_id = str(uuid.uuid4())
        db.add(user)
        db.commit()
        db.refresh(user)
        return {"username": user.username, "user_id": user.user_id}

@app.post("/login/")
async def login(username: str, password: str):
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    else:
        if bcrypt.verify(password, user.password):
            return {"username": user.username, "user_id": user.user_id}
        else:
            raise HTTPException(status_code=401, detail="incorrect password")

@app.post("/users/{user_id}/soil_data/", response_model=SoilData)
async def create_soil_data(user_id: str, soil_data: SoilDataCreate):
    db = SessionLocal()
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    else:
        soil_data = SoilData(**soil_data.dict())
        soil_data.user_id = user_id
        db.add(soil_data)
        db.commit()
        db.refresh(soil_data)
        return {"message": "soil data saved successfully"}

@app.get("/users/{user_id}/soil_data/")
async def get_soil_data(user_id: str):
    db = SessionLocal()
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    else:
        soil_data = db.query(SoilData).filter(SoilData.user_id == user_id).all()
        if not soil_data:
            raise HTTPException(status_code=404, detail="soil data not found")
        else:
            soil_data_dict = [data.__dict__ for data in soil_data]
            soil_data_dict = [{key: value for key, value in data.items() if not key.startswith("_")} for data in soil_data_dict]
            with open('soil_data.csv', mode='w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=soil_data_dict[0].keys())
                writer.writeheader()
                for data in soil_data_dict:
                    writer.writerow(data)
            return FileResponse('soil_data.csv', media_type='text/csv', filename='soil_data.csv')

@app.post("/users/{user_id}/soil_recommends/", response_model=SoilRecommends)
async def create_soil_recommends(user_id: str, soil_recommends: SoilRecommendsCreate):
    db = SessionLocal()
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    else:
        soil_Recommends = SoilRecommends(**soil_recommends.dict())
        soil_recommends.user_id = user_id
        db.add(soil_recommends)
        db.commit()
        db.refresh(soil_recommends)
        return {"message": "soil recommends saved successfully"}

@app.get("/users/{user_id}/soil_recommends/")
async def get_soil_recommends(user_id: str):
    db = SessionLocal()
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    else:
        soil_recommends = db.query(SoilRecommends).filter(SoilRecommends.user_id == user_id).all()
        if not soil_recommends:
            raise HTTPException(status_code=404, detail="soil data not found")
        else:
            soil_data_dict = [data.__dict__ for data in soil_recommends]
            soil_data_dict = [{key: value for key, value in data.items() if not key.startswith("_")} for data in soil_data_dict]
            with open('soil_data.csv', mode='w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=soil_data_dict[0].keys())
                writer.writeheader()
                for data in soil_data_dict:
                    writer.writerow(data)
            return FileResponse('soil_data.csv', media_type='text/csv', filename='soil_recomends.csv')

