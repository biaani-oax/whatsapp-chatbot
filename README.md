
Para clonar este repo, en terminal:
gh auth login

Después de logearse:
gh repo clone biaani-oax/whatsapp-chatbot

Depués entrar y crear entorno virtual:
cd whatsapp-chatbot
Windows:
py -m venv .venv
.\.venv\Scripts\Activate.ps1

Se verá (.venv) al inicio de cada comando. Ahora hacemos requirements.txt (con un upgrade pip antes):
py -m pip install --upgrade pip
py -m pip install -r requirements.txt

Ahora nos aseguramos que ngrok esté corriendo:
https://dashboard.ngrok.com/get-started/share-localhost

Ahí asegurarse que está el authtoken (en este caso me sale así, revisar en darle show)
ngrok config add-authtoken 3LXO5HtYjQ0HxveChQEVZgy5tXy_6AtSMjkkyiCKQdVP4GGBj
Ojo: no debe verse así!!: ngrok config add-authtoken $YOUR_AUTHTOKEN
(puede que ya esté, saldrá un mensaje que ya se encuentra en ngrok.yml

Ahora, correr ngrok (pueden hacerlo en una nueva ventana de cmd, powershell está fallando!):
ngrok http 8000 --url https://flaky-stout-cheesy.ngrok-free.dev

Hay que crear el archivo .env en raíz
META_VERIFY_TOKEN=meta_verificacion_2026
META_ACCESS_TOKEN="EL TOKEN GENERADO EN META"
WHATSAPP_PHONE_NUMBER_ID=1421526587712629
OLLAMA_MODEL=llama3.1:8b

Ahora ya se puede correr el uvicorn de fastapi:
uvicorn app.api:app --reload --host 0.0.0.0 --port 8000

No se olvide de cambiar en llm.py:
        options={
            "temperature": 0.2,
            "num_ctx": 8192,
            "num_predict": 300
        }
    )
Probar para que no alucine y responda rápido
Además, cambiar el modelo en .env (al final) y en main:
    parser.add_argument(
        "--model",
        type=str,
        default="llama3.1:8b",
        help="Modelo de Ollama que utilizará el chatbot"
    )
