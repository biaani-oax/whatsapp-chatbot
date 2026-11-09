import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")

async def post_init(application):
    me = await application.bot.get_me()
    print(f"Conectado correctamente: @{me.username}")

app = (
    ApplicationBuilder()
    .token(TOKEN)
    .post_init(post_init)
    .build()
)

print("Iniciando prueba de Telegram...")
app.run_polling()