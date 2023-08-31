from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from hugchat import hugchat
from hugchat.login import Login
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import csv
import tempfile
import os

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

class Message(BaseModel):
    message: str

class User(BaseModel):
    username: str

class SoilData(BaseModel):
    date_time: str
    soil_name: str
    nitrogen: float
    phosphorus: float
    potassium: float
    moisture: int
    temperature: float

class SoilRecommends(BaseModel):
    date_time: str
    soil_name: str
    crop_name: str
    soil_area: float
    nitrogen: float
    phosphorus: float
    potassium: float
    recommendations: str

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


@app.post("/users/")
async def create_user(user: User):
    user_id = str(hash(user.username))
    user_dir = f"./users/{user_id}"
    if os.path.exists(user_dir):
        raise HTTPException(status_code=400, detail="existing username error")
    else:
        os.makedirs(user_dir)
        with open(f"{user_dir}/soil_data.csv", mode='w') as soil_data_file:
            fieldnames = ['date_time', 'soil_area', 'nitrogen', 'phosphorus', 'potassium', 'moisture', 'temperature']
            writer = csv.DictWriter(soil_data_file, fieldnames=fieldnames)
            writer.writeheader()
        with open(f"{user_dir}/soil_recommends.csv", mode='w') as soil_recommends_file:
            fieldnames = ['date_time', 'soil_name', 'crop_name', 'soil_area', 'nitrogen', 'phosphorus', 'potassium', 'recommendations']
            writer = csv.DictWriter(soil_recommends_file, fieldnames=fieldnames)
            writer.writeheader()
        return {"user_id": user_id}

@app.post("/users/{user_id}/soil_data/")
async def create_soil_data(user_id: str, soil_data: SoilData):
    user_dir = f"./users/{user_id}"
    if not os.path.exists(user_dir):
        raise HTTPException(status_code=404, detail="user not found")
    else:
        with open(f"{user_dir}/soil_data.csv", mode='a') as soil_data_file:
            fieldnames = ['date_time', 'soil_name', 'nitrogen', 'phosphorus', 'potassium', 'moisture', 'temperature']
            writer = csv.DictWriter(soil_data_file, fieldnames=fieldnames)
            writer.writerow(soil_data.dict())
        return {"message": "soil data saved successfully"}

@app.get("/users/{user_id}/soil_data/")
async def get_soil_data(user_id: str):
    user_dir = f"./users/{user_id}"
    if not os.path.exists(user_dir):
        raise HTTPException(status_code=404, detail="user not found")
    else:
        file_path = f"{user_dir}/soil_data.csv"
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="soil data not found")
        else:
            return FileResponse(file_path, media_type="text/csv", filename="soil_data.csv")
        
@app.post("/users/{user_id}/soil_recommends/")
async def create_soil_recommends(user_id: str, soil_recommends: SoilRecommends):
    user_dir = f"./users/{user_id}"
    if not os.path.exists(user_dir):
        raise HTTPException(status_code=404, detail="user not found")
    else:
        with open(f"{user_dir}/soil_recommends.csv", mode='a') as soil_recommends_file:
            fieldnames = ['date_time', 'soil_name', 'crop_name', 'soil_area', 'nitrogen', 'phosphorus', 'potassium', 'recommendations']
            writer = csv.DictWriter(soil_recommends_file, fieldnames=fieldnames)
            writer.writerow(soil_recommends.dict())
        return {"message": "soil data saved successfully"}
    
@app.get("/users/{user_id}/soil_recommends/")
async def get_soil_data(user_id: str):
    user_dir = f"./users/{user_id}"
    if not os.path.exists(user_dir):
        raise HTTPException(status_code=404, detail="user not found")
    else:
        file_path = f"{user_dir}/soil_recommends.csv"
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="soil data not found")
        else:
            return FileResponse(file_path, media_type="text/csv", filename="soil_recommends.csv")