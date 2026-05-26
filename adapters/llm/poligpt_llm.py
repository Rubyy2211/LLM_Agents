from __future__ import annotations
import time
 
 
class PoliGPTLLM:
    """Implementa LLMPort estructuralmente."""
 
    def __init__(self, base_url: str, api_key: str, model: str = "poligpt") -> None:
        from openai import OpenAI
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = model
 
    def generate(self, prompt: str, *, temperature: float = 0.2) -> tuple[str, dict]:
        t0 = time.time()
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )
        elapsed = time.time() - t0
        text = resp.choices[0].message.content or ""
        usage = resp.usage
        prompt_tokens = usage.prompt_tokens if usage else 0
        output_tokens = usage.completion_tokens if usage else 0
        tokens_per_sec = round(output_tokens / elapsed, 2) if elapsed > 0 else 0.0
        metricas = {
            "prompt_tokens": prompt_tokens,
            "output_tokens": output_tokens,
            "tokens_per_sec": tokens_per_sec,
            "latencia_s": round(elapsed, 2),
            "modelo": self.model,
        }
        return text, metricas