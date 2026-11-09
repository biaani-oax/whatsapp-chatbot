import asyncio
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters,
)

from app.llm import generate_response, OLLAMA_MODEL

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
MAX_MENSAJES = 10   # historial que se conserva por chat (tu num_ctx es 4096)

HISTORIAL = {}      # chat_id -> lista de mensajes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Hola! Soy el asistente de Biaani. ¿En qué te puedo ayudar?")


async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    mensajes = HISTORIAL.setdefault(chat_id, [])
    mensajes.append({"role": "user", "content": update.message.text})
    del mensajes[:-MAX_MENSAJES]

    await context.bot.send_chat_action(chat_id, "typing")
    try:
        # generate_response es síncrona: se manda a un hilo para no bloquear el bot
        respuesta = await asyncio.to_thread(generate_response, mensajes, OLLAMA_MODEL)
    except Exception as e:
        print("Error con el LLM:", e)
        mensajes.pop()
        await update.message.reply_text("Tuve un problema al generar la respuesta. Intenta de nuevo.")
        return

    mensajes.append({"role": "assistant", "content": respuesta})
    await update.message.reply_text(respuesta)


def construir_app():
    if not TELEGRAM_TOKEN:
        raise SystemExit("Falta TELEGRAM_TOKEN en el .env")
    tg = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    tg.add_handler(CommandHandler("start", start))
    tg.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
    return tg


if __name__ == "__main__":
    print("Bot de Telegram en marcha (polling)...")
    construir_app().run_polling()