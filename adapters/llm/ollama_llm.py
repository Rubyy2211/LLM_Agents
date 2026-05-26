"""Adapter LLM → Ollama local."""
from __future__ import annotations
import time
import urllib3
import requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class OllamaLLM:
    """Implementa LLMPort estructuralmente (Protocol, no herencia)."""
 
    def __init__(self, base_url: str, model: str, verify_ssl: bool = True) -> None:
        self.base_url = base_url
        self.model = model
        self.verify_ssl = verify_ssl
 
    def generate(self, prompt: str, *, temperature: float = 0.2) -> tuple[str, dict]:
        t0 = time.time()
        response = requests.post(
            f"{self.base_url}/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": temperature},
            },
            verify=self.verify_ssl,
            timeout=180,
        )
        elapsed = time.time() - t0
        response.raise_for_status()
        payload = response.json()
 
        prompt_tokens = int(payload.get("prompt_eval_count", 0))
        output_tokens = int(payload.get("eval_count", 0))
        eval_duration_ns = int(payload.get("eval_duration", 0))
        tokens_per_sec = (
            output_tokens / (eval_duration_ns / 1e9) if eval_duration_ns > 0 else 0.0
        )
        metricas = {
            "prompt_tokens": prompt_tokens,
            "output_tokens": output_tokens,
            "tokens_per_sec": round(tokens_per_sec, 2),
            "latencia_s": round(elapsed, 2),
            "modelo": self.model,
        }
        return payload["response"], metricas
 