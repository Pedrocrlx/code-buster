from pathlib import Path

import httpx
import pytest
from settings import OLLAMA_BASE_URL

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _ollama_running() -> bool:
    try:
        httpx.get(OLLAMA_BASE_URL, timeout=2)
        return True
    except Exception:
        return False


ollama = pytest.mark.skipif(not _ollama_running(), reason="Ollama not running")

HARDCODED_MDS = [
    (FIXTURES_DIR / "resolved.md").read_text(),
    (FIXTURES_DIR / "unresolved.md").read_text(),
]

AI_ENTRY = (FIXTURES_DIR / "pending_processing.md").read_text().strip()
