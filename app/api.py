import os
from contextlib import asynccontextmanager

import httpx
from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse

from app.telegram_bot import construir_app

load_dotenv()  # primero se lee el .env, y solo después las variables

# --- Configuración ---
VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN")
WHATSAPP_TOKEN = os.getenv("META_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
GRAPH_VERSION = os.getenv("GRAPH_VERSION", "v26.0")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

SYSTEM_PROMPT = (
    "Eres el asistente de Biaani Academia STEAM. "
    "Responde siempre en español, de forma clara y breve (máximo 3 oraciones)."
)

for nombre, valor in [
    ("META_VERIFY_TOKEN", VERIFY_TOKEN),
    ("META_ACCESS_TOKEN", WHATSAPP_TOKEN),
    ("WHATSAPP_PHONE_NUMBER_ID", PHONE_NUMBER_ID),
]:
    if not valor:
        print(f"AVISO: falta {nombre} en el .env")

VISTOS = set()  # ids de mensajes ya atendidos (suficiente para la demo)


# --- Arranque/cierre: aquí se enciende el bot de Telegram ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    tg = construir_app()
    await tg.initialize()
    await tg.start()
    await tg.updater.start_polling()
    yield
    await tg.updater.stop()
    await tg.stop()
    await tg.shutdown()


# --- La app (una sola, con lifespan) ---
app = FastAPI(
    title="Biaani Chatbot API",
    description="Webhook y API del chatbot Biaani",
    version="1.0.0",
    lifespan=lifespan,
)


# --- Funciones auxiliares ---
async def preguntar_llm(texto: str) -> str:
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(f"{OLLAMA_URL}/api/chat", json={
            "model": OLLAMA_MODEL,
            "stream": False,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": texto},
            ],
        })
        r.raise_for_status()