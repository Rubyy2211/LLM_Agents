"""FakeLLM para tests del dominio sin red."""
from __future__ import annotations
 
 
class FakeLLM:
    """Devuelve respuestas prefijadas. No requiere red."""
 
    def __init__(self, response: str = "Respuesta de prueba") -> None:
        self.response = response
 
    def generate(self, prompt: str, *, temperature: float = 0.2) -> tuple[str, dict]:
        metricas = {
            "prompt_tokens": len(prompt.split()),
            "output_tokens": len(self.response.split()),
            "tokens_per_sec": 999.0,
            "latencia_s": 0.001,
            "modelo": "fake",
        }
        return self.response, metricas