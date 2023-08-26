from fastapi import FastAPI
from pydantic import BaseModel
from hugchat import hugchat
from hugchat.login import Login

app = FastAPI()

class Message(BaseModel):
    message: str

sign = Login("gsarmiento0798@gmail.com", "Blankshounen_30")
cookies = sign.login()

# Save cookies to the local directory
cookie_path_dir = "./cookies_snapshot"
sign.saveCookiesToDir(cookie_path_dir)

@app.put("/message")
async def update_message(message: Message):
    # Log in to huggingface and grant authorization to huggingchat

    # Create a ChatBot
    chatbot = hugchat.ChatBot(cookies=cookies.get_dict())

    # Get a response from the chatbot
    response = chatbot.chat(message.message)

    return {"response": response}