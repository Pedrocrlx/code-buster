import os

# ── Ollama ─────────────────────────────────────────────────────────────────

# Model reference, change to upgrade model to a more powerful one
OLLAMA_MODEL_NAME = os.environ.get("OLLAMA_MODEL", "qwen2.5:1.5b")

# Full model name for API calls, including 'ollama/' prefix, required by the API
OLLAMA_MODEL = f"ollama/{OLLAMA_MODEL_NAME}"

# Reinforces the localhost URL for Ollama, change for custom setups (DANGER)
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

# ── Application paths ──────────────────────────────────────────────────────

# Directory to store user-generated bust MD files
BUSTS_DIR_NAME = ".busts"

# Name for the SQLite Database file
DB_FILENAME = "busts.db"

# Prefix of the filename for MD busts
BUST_PREFIX = "bust_"

# ── Recall tuning ──────────────────────────────────────────────────────────

# Raise for stricter matches, lower to 1 for broader (but noisier) recall
# Too high may lead to no matches found, too low may lead to irrelevant matches
RECALL_MIN_KEYWORD_MATCHES = 2
