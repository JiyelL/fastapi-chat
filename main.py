from io import BytesIO
from typing import List, Dict, Any, List
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from pydantic import BaseModel
from hugchat import hugchat
from hugchat.login import Login
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import csv
import tempfile
import os
import pandas as pd

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

user_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
    },
    "required": ["name"]
}

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

soil_recommends_schema = {
    "type": "object",
    "properties": {
        "soil_name": {"type": "string"},
        "crop_name": {"type": "string"},
        "soil_area": {"type": "string"},
        "nitrogen": {"type": "string"},
        "phosphorus": {"type": "string"},
        "potassium": {"type": "string"},
        "recommendation": {"type": "string"}
    },
    "required": ["soil_name", "crop_name", "soil_area", "nitrogen", "phosphorus", "potassium", "recommendation"]
}

# Define a list to store the users
users = []

# Define a list to store the soil data
soil_data = []


@app.post("/users/")
async def create_user(user: dict):
    # Validate the user data
    if not user["name"]
        raise ValueError("Please provide all required fields")
    
    # Check if the user already exists
    existing_user = next((user for user in users if user["name"] == user["name"]), None)
    if existing_user:
        raise ValueError("A user with this username already exists")
    
    # Add the user to the list
    user_id = len(users) + 1
    users.append({**user, "id": user_id})
    
    # Return the created user
    return JSONResponse(content=user, status_code=201)


@app.post("/soil/")
async def create_soil_data(soil_data: dict):
    # Validate the soil data
    if not soil_data["soil_name"] or not soil_data["crop_name"] or not soil_data["soil_area"] or \
       not soil_data["nitrogen"] or not soil_data["phosphorus"] or not soil_data["potassium"] or \
       not soil_data["recommendation"]:
        raise ValueError("Please provide all required fields")
    
    # Add the soil data to the list
    soil_data_id = len(soil_data) + 1
    soil_data.append({**soil_data, "id": soil_data_id})
    
    # Return the created soil data
    return JSONResponse(content=soil_data, status_code=201)


@app.get("/users/")
async def get_all_users():
    # Return all the users
    return JSONResponse(content=users, status_code=200)


@app.get("/soil/")
async def get_all_soil_data():
    # Return all the soil data
    return JSONResponse(content=soil_data, status_code=200)

@app.post("/soil/<int:soil_data_id>")
async def save_soil_data(soil_data_id: int, soil_data: dict):
    # Find the soil data with the given ID
    soil_data = next((soil_data for soil_data in soil_data if soil_data["id"] == soil_data_id), None)
    
    # Validate the soil data
    if not soil_data:
        raise ValueError("Soil data not found")
    
    # Save the soil data to a CSV file
    with open("soil_data.csv", "a") as csvfile:
        fieldnames = ["soil_name", "crop_name", "soil_area", "nitrogen", "phosphorus", "potassium", "recommendation"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow(soil_data)
    
    # Return a message indicating that the data has been saved successfully
    return JSONResponse(content={"message": "Soil data saved successfully"}, status_code=201)

@app.get("/soil/<int:soil_data_id>/download")
async def download_soil_data(soil_data_id: int):
    # Find the soil data with the given ID
    soil_data = next((soil_data for soil_data in soil_data if soil_data["id"] == soil_data_id), None)
    
    # Validate the soil data
    if not soil_data:
        raise ValueError("Soil data not found")
    
    # Open the CSV file and read its contents
    with open("soil_data.csv", "r") as csvfile:
        reader = csv.DictReader(csvfile)
        soil_data_row = next((row for row in reader if row["id"] == soil_data_id), None)
        
    # Create a BytesIO object to hold the CSV data
    buffer = BytesIO()
    writer = csv.DictWriter(buffer, fieldnames=reader.fieldnames)
    writer.writerow(soil_data_row)
    buffer.seek(0)
    
    # Send the CSV data as a downloadable attachment
    return Response(body=buffer, content_type="text/csv", filename="soil_data_{}.csv".format(soil_data_id))