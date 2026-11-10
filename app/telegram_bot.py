import os

from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)

from app.conversation import process_incoming_message


load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "¡Hola! Soy el asistente de Biaani. "
        "¿En qué te puedo ayudar?"
    )


async def responder(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    usuario = update.effective_user
    mensaje = update.message

    if not usuario or not mensaje or not mensaje.text:
        return

    nombre = " ".join(
        parte for parte in [usuario.first_name, usuario.last_name]
        if parte
    )

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )

    try:
        respuesta = await process_incoming_message(
            platform="telegram",
            platform_user_id=str(usuario.id),
            display_name=nombre or None,
            text=mensaje.text,
            platform_message_id=f"{usuario.id}:{mensaje.message_id}"
        )

        # Un mensaje duplicado no genera otra respuesta
        if respuesta is not None:
            await mensaje.reply_text(respuesta)

    except Exception as e:
        print("Error procesando mensaje de Telegram:", e)

        await mensaje.reply_text(
            "Tuve un problema al procesar tu mensaje. "
            "Intenta de nuevo."
        )


def construir_app():

    if not TELEGRAM_TOKEN:
        raise RuntimeError("Falta TELEGRAM_TOKEN en el archivo .env")

    tg = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    tg.add_handler(CommandHandler("start", start))

    tg.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            responder
        )
    )

    return tg


if __name__ == "__main__":
    print(
        "Este módulo se inicia desde api.py "
        "o puede ejecutarse de forma independiente."
    )

    construir_app().run_polling()