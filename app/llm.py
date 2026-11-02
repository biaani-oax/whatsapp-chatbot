import ollama

SYSTEM_PROMPT = """
Eres el asistente virtual de Biaani, un centro STEM Maker.

Tu función es orientar a los usuarios sobre los servicios,
talleres, actividades y funcionamiento de la academia.

Responde en español, de forma clara, amable y precisa.

Si no tienes información suficiente para responder,
indica que no cuentas con ese dato. No inventes información.
"""

def generate_response(messages: list, model: str) -> str:
    response = ollama.chat(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
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