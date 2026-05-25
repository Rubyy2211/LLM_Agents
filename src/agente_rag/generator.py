"""Cliente HTTP para generación (Ollama) con captura de métricas.

Devuelve respuesta + las 4 métricas que el enunciado pide para banda 7:
- prompt_tokens
- output_tokens
- tokens_per_sec
- latencia_s

Se calculan a partir del JSON nativo de Ollama (``prompt_eval_count``,
``eval_count``, ``eval_duration``) más un cronómetro de pared como red de
seguridad si el servidor no devolviera los campos.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

import urllib3
import requests

from .config import SETTINGS


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@dataclass
class Generation:
    text: str
    prompt_tokens: int
    output_tokens: int
    tokens_per_sec: float
    latency_s: float
    model: str


def generate(prompt: str, *, temperature: float = 0.2, model: str | None = None) -> Generation:
    chosen_model = model or SETTINGS.llm_model
    t0 = time.time()
    response = requests.post(
        f"{SETTINGS.ollama_url}/generate",
        json={
            "model": chosen_model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature},
        },
        verify=SETTINGS.verify_ssl,
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

    return Generation(
        text=payload["response"],
        prompt_tokens=prompt_tokens,
        output_tokens=output_tokens,
        tokens_per_sec=round(tokens_per_sec, 2),
        latency_s=round(elapsed, 2),
        model=chosen_model,
    )
