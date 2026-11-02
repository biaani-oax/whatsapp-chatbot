import ollama

MODEL = "qwen3.5:9b-q4_K_M"

SYSTEM_PROMPT = """
Eres el asistente virtual de Biaani, un centro STEM Maker.

Tu función es orientar a los usuarios sobre los servicios,
talleres, actividades y funcionamiento de la academia.

Responde en español, de forma clara, amable y precisa.

Si no tienes información suficiente para responder,
indica que no cuentas con ese dato. No inventes información.
"""


def generate_response(messages: list) -> str:

    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            *messages
        ]
    )

    return response["message"]["content"]
