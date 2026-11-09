import os
import asyncio
import httpx

from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse

load_dotenv()  # primero se lee el .env, y solo después las variables

from app.telegram_bot import construir_app
from app.llm import generate_response
# ==========================================
# CONFIGURACIÓN
# ==========================================
VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN")   # usa el nombre que ya tengas en tu .env
WHATSAPP_TOKEN = os.getenv("META_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

GRAPH_VERSION = os.getenv("GRAPH_VERSION", "v26.0")

VISTOS = set()  # ids de mensajes ya atendidos (suficiente para la demo)
# ==========================================
# INICIALIZACIÓN DE TELEGRAM
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):

    tg = construir_app()

    await tg.initialize()
    await tg.start()
    await tg.updater.start_polling()

    app.state.telegram_app = tg

    try:
        yield

    finally:
        await tg.updater.stop()
        await tg.stop()
        await tg.shutdown()
# ==========================================
# APLICACIÓN FASTAPI
# ==========================================
app = FastAPI(
    title="Biaani Chatbot API",
    description="Webhook y API del chatbot Biaani",
    version="1.0.0",
    lifespan=lifespan
)

# --- Funciones auxiliares ---

def normalizar_mx(numero: str) -> str:
    # El webhook entrega 521 + 10 dígitos; la lista de destinatarios usa 52 + 10 dígitos
    if numero.startswith("521") and len(numero) == 13:
        return "52" + numero[3:]
    return numero

# ==========================================
# ENVÍO DE MENSAJES A WHATSAPP
# ==========================================
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
# ==========================================
# PROCESAMIENTO DE MENSAJES
# ==========================================
async def procesar(data: dict):
    for entry in data.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            for msg in value.get("messages", []):
                if msg.get("type") != "text" or msg["id"] in VISTOS:
                    continue
                VISTOS.add(msg["id"])
                try:
                    respuesta = await asyncio.to_thread(
                        generate_response,
                        [{"role": "user", "content": msg["text"]["body"]}],
                    )
                    respuesta = respuesta.strip()
                except Exception as e:
                    print("Error con el LLM:", e)
                    respuesta = "Tuve un problema al generar la respuesta. Intenta de nuevo."
                await enviar_whatsapp(msg["from"], respuesta)

# ==========================================
# VERIFICACIÓN DEL WEBHOOK DE META
# ==========================================
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
# ==========================================
# RECEPCIÓN DE MENSAJES DE WHATSAPP
# ==========================================
@app.post("/webhook")
async def receive_webhook(request: Request, background: BackgroundTasks):
    data = await request.json()
    print("\nEvento recibido:", data)
    background.add_task(procesar, data)
    return {"status": "received"}

