"""Adapter embedder → Ollama."""
from __future__ import annotations
import urllib3
import requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
 
 
class OllamaEmbedder:
    """Implementa EmbedderPort estructuralmente."""
 
    def __init__(self, base_url: str, model: str, verify_ssl: bool = True) -> None:
        self.base_url = base_url
        self.model = model
        self.verify_ssl = verify_ssl
 
    def embed(self, text: str) -> list[float]:
        response = requests.post(
            f"{self.base_url}/embeddings",
            json={"model": self.model, "prompt": text},
            verify=self.verify_ssl,
            timeout=60,
        )
        response.raise_for_status()
        return response.json()["embedding"]