from typing import List, Dict, Any
from fastapi import FastAPI
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

@app.put("/create_csv/")
async def create_csv(data: List[Dict[str, Any]]):
    # Create a list of dictionaries from the data
    data_list = [dict(row) for row in data]
    # Create a temporary CSV file
    with open('temp.csv', mode='w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=data_list[0].keys())
        writer.writeheader()
        writer.writerows(data_list)
    # Return the CSV file as a downloadable response
    return FileResponse('temp.csv', media_type='text/csv', filename='data.csv', headers={'Content-Disposition': 'attachment; filename=data.csv'})