
import ollama
import os

from dotenv import load_dotenv

load_dotenv()


# Configuración centralizada
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")

SYSTEM_PROMPT = """
Eres el asistente virtual de Biaani, un centro STEM Maker.

Tu función es orientar a los usuarios sobre los servicios,
talleres, actividades y funcionamiento de la academia.

Responde siempre en español, de forma breve, clara, amable y precisa.

Si no tienes información suficiente para responder,
indica que no cuentas con ese dato. No inventes información.
"""


def generate_response(
    messages: list,
    model: str = None,
    company_context: dict = None
) -> str:

    model = model or OLLAMA_MODEL

    # Construir el contexto empresarial
    context_text = ""

    if company_context:
        context_text = "\n\nINFORMACIÓN OFICIAL DE BIAANI:\n"

        for key, item in company_context.items():
            context_text += (
                f"\n{key}: {item['content']}"
            )

    system_message = {
        "role": "system",
        "content": SYSTEM_PROMPT + context_text
    }

    response = ollama.chat(
        model=model,
        messages=[
            system_message,
            *messages
        ],
        think=False,
        options={
            "temperature": 0.2,
            "num_ctx": 4096,
            "num_predict": 300
        }
    )

    return response["message"]["content"]
