"""Configuración global de pytest.

Añadimos ``src/`` al ``sys.path`` para que los tests importen el paquete
``agente_rag`` igual que lo importa el corrector tras un ``pip install -e .``.
Así el repo es ejecutable sin instalar.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT))
