import requests
from domain.ports import LLMPort

class OllamaLLM: # implementa LLMPort estructuralmente
    def __init__(self, base_url: str, model: str):
        self.base_url = base_url
        self.model = model

    def generate(self, prompt: str, *, temperature: float = 0.2)-> str:
        r = requests.post(f"{self.base_url}/generate", json={
            "model": self.model, "prompt": prompt,
            "stream": False, "options": {"temperature": temperature}
        })
        return r.json()["response"]