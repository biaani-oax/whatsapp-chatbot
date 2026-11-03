import os

import httpx
from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse

load_dotenv()  # primero se lee el .env, y solo después las variables

# --- Configuración ---
VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN")   # usa el nombre que ya tengas en tu .env
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
    ("WHATSAPP_VERIFY_TOKEN", VERIFY_TOKEN),
    ("WHATSAPP_ACCESS_TOKEN", WHATSAPP_TOKEN),
    ("WHATSAPP_PHONE_NUMBER_ID", PHONE_NUMBER_ID),
]:
    if not valor:
        print(f"AVISO: falta {nombre} en el .env")

VISTOS = set()  # ids de mensajes ya atendidos (suficiente para la demo)

# --- La app (debe existir antes de usar @app) ---
app = FastAPI(
    title="Biaani Chatbot API",
    description="Webhook y API del chatbot Biaani",
    version="1.0.0",
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
        return r.json()["message"]["content"].strip()

def normalizar_mx(numero: str) -> str:
    # El webhook entrega 521 + 10 dígitos; la lista de destinatarios usa 52 + 10 dígitos
    if numero.startswith("521") and len(numero) == 13:
        return "52" + numero[3:]
    return numero

async def enviar_whatsapp(destino: str, texto: str):
    destino = normalizar_mx(destino)
    url = f"https://graph.facebook.com/{GRAPH_VERSION}/{PHONE_NUMBER_ID}/messages"
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            url,
            headers={"Authorization": f"Bearer {WHATSAPP_TOKEN}"},
            json={
                "messaging_product": "whatsapp",
                "to": destino,
                "type": "text",
                "text": {"body": texto[:4000]},
            },
        )
        print("Envío a WhatsApp:", r.status_code, r.text)


async def procesar(data: dict):
    for entry in data.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            for msg in value.get("messages", []):
                if msg.get("type") != "text" or msg["id"] in VISTOS:
                    continue
                VISTOS.add(msg["id"])
                try:
                    respuesta = await preguntar_llm(msg["text"]["body"])
                except Exception as e:
                    print("Error con el LLM:", e)
                    respuesta = "Tuve un problema al generar la respuesta. Intenta de nuevo."
                await enviar_whatsapp(msg["from"], respuesta)


# --- Rutas ---
@app.get("/")
def home():
    return {"status": "online", "application": "Biaani Chatbot"}


@app.get("/webhook")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return PlainTextResponse(challenge)

    raise HTTPException(status_code=403, detail="Verificación incorrecta")


@app.post("/webhook")
async def receive_webhook(request: Request, background: BackgroundTasks):
    data = await request.json()
    print("\nEvento recibido:", data)
    background.add_task(procesar, data)
    return {"status": "received"}