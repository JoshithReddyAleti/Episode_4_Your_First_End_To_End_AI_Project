"""
utils/config.py — Configuration Management
============================================
AI Engineering Roadmap 2026 · Episode 3

All configuration comes from environment variables.
This is a non-negotiable production engineering practice.

Why?
  - API keys must NEVER be hardcoded in source files
  - Different environments (dev, staging, prod) need different values
  - .env files are excluded from git (see .gitignore)

Call load_config() once at startup (in main.py).
Every other module reads from os.environ directly.
"""

import os
from pathlib import Path
from app.utils.logger import get_logger

logger = get_logger(__name__)


def load_config(env_path: str = ".env") -> None:
    """
    Load environment variables from a .env file.

    Falls back gracefully if the .env file doesn't exist
    (useful in CI environments where env vars are injected directly).

    Args:
        env_path: Path to the .env file (default: .env in project root)
    """
    env_file = Path(env_path)

    if env_file.exists():
        _load_dotenv(env_file)
        logger.info(f"Config loaded from {env_file.resolve()}")
    else:
        logger.warning(
            f".env file not found at {env_file.resolve()}. "
            f"Relying on system environment variables. "
            f"Copy .env.example to .env and fill in your keys."
        )

    _validate_required_keys()


def _load_dotenv(path: Path) -> None:
    """
    Parse a .env file and set values as environment variables.
    Uses python-dotenv if available, otherwise falls back to manual parsing.
    """
    try:
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=path, override=False)
    except ImportError:
        # Manual fallback — reads KEY=VALUE lines
        logger.debug("python-dotenv not found, using manual .env parser.")
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = value


def _validate_required_keys() -> None:
    """
    Warn (not crash) if required environment variables are missing.
    This gives a helpful message instead of a cryptic KeyError later.
    """
    required = {
        "OPENAI_API_KEY": "Required to call the LLM. Get yours at https://platform.openai.com",
    }

    optional = {
        "LLM_MODEL": "Defaults to gpt-4o-mini if not set.",
        "LOG_LEVEL": "Defaults to INFO if not set.",
    }

    for key, hint in required.items():
        if not os.environ.get(key):
            logger.warning(f"Missing required config: {key}. {hint}")

    for key, hint in optional.items():
        if not os.environ.get(key):
            logger.debug(f"Optional config not set: {key}. {hint}")
