import os
import ollama

from dotenv import load_dotenv

load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")


SYSTEM_PROMPT = """
Eres el asistente virtual de Biaani, un centro STEM Maker.

Tu función es orientar a los usuarios sobre los servicios,
talleres, actividades y funcionamiento de la academia.

Responde en español, de forma breve, clara, amable y precisa.

Utiliza la información oficial proporcionada en el contexto
empresarial y el historial de la conversación.

No inventes horarios, precios, servicios, ubicaciones ni políticas.

Si no tienes información suficiente para responder,
indica claramente que no cuentas con ese dato.

Procura responder de forma breve y directa.
"""


def generate_response(
    messages: list,
    model: str = None,
    company_context: dict = None,
    conversation_summary: str = ""
) -> str:

    model = model or OLLAMA_MODEL

    # Construir el contexto empresarial
    context_text = ""

    if company_context:
        context_text += "\n\nINFORMACIÓN OFICIAL DE BIAANI:\n"

        for key, item in company_context.items():
            context_text += (
                f"\nCategoría: {item['category']}"
                f"\nTema: {key}"
                f"\nInformación: {item['content']}\n"
            )

    # Incorporar resumen si existe
    if conversation_summary:
        context_text += (
            "\n\nRESUMEN DE LA CONVERSACIÓN ANTERIOR:\n"
            + conversation_summary
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
            "num_predict": 200
        }
    )

    return response["message"]["content"]