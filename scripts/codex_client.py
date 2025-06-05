# scripts/codex_client.py

import os
from dotenv import load_dotenv
import openai

# 1) Definimos base_dir apuntando a la raíz del proyecto
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(base_dir, ".env.local")  # O .env si usas ese nombre
load_dotenv(dotenv_path)

# 2) Configuramos la clave de OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

def generar_codigo(prompt: str,
                   model: str = "gpt-3.5-turbo",
                   temperatura: float = 0.0,
                   max_tokens: int = 512) -> str:
    """
    Llama al endpoint de Chat Completions (Codex) de OpenAI para generar fragmentos de código.
    - prompt: string con la instrucción en lenguaje natural.
    - model: "gpt-3.5-turbo" por defecto (asegúrate de tener crédito).
      Si tu cuenta tiene acceso a "gpt-4o", puedes cambiarlo a "gpt-4o".
    - temperatura: entre 0.0 y 1.0, para código conviene 0.0 o 0.1.
    - max_tokens: máxima longitud de la respuesta.
    Devuelve: string con el código generado.
    """
    # Generamos un mensaje “system” donde le damos el contexto de tu infra:
    system_content = (
        "Eres un asistente experto en proyectos Django + React.\n"
        f"DATABASE_URL={os.getenv('DATABASE_URL')}\n"
        f"STATIC_SERVICE_URL={os.getenv('STATIC_SERVICE_URL')}\n"
        f"STATIC_SERVICE_API_KEY={os.getenv('STATIC_SERVICE_API_KEY')}\n"
    )

    respuesta = openai.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user",   "content": prompt}
        ],
        temperature=temperatura,
        max_tokens=max_tokens,
        n=1
    )
    return respuesta.choices[0].message.content.strip()
