import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

base_url = os.environ.get("POLIGPT_BASE_URL")
api_key = os.environ.get("POLIGPT_API_KEY")
if not base_url or not api_key:
    raise RuntimeError(
        "Faltan variables de entorno POLIGPT_BASE_URL o POLIGPT_API_KEY. "
        "Asegúrate de que .env existe y contiene estas claves."
    )

client = OpenAI(
    base_url=base_url,
    api_key=api_key,
)
resp = client.chat.completions.create(
    model="poligpt",
    messages=[{"role": "user", "content": "Hola"}],
    temperature=0.2,
)
print(resp.choices[0].message.content)
