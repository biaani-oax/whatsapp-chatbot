from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse

from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(
    title="Biaani Chatbot API",
    description="Webhook y API del chatbot Biaani",
    version="1.0.0"
)

VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN")


@app.get("/")
def home():

    return {
        "status": "online",
        "application": "Biaani Chatbot"
    }


@app.get("/webhook")
async def verify_webhook(request: Request):

    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:

        return PlainTextResponse(challenge)

    raise HTTPException(
        status_code=403,
        detail="Verificación incorrecta"
    )


@app.post("/webhook")
async def receive_webhook(request: Request):

    data = await request.json()

    print("\nEvento recibido:")
    print(data)

    return {"status": "received"}