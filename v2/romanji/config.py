"""The only place that reads settings and secrets (v2/.env via python-dotenv).

A missing GENIUS_ACCESS_TOKEN is not an error here; call
`require_genius_token(settings)` in Genius mode only.
"""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import dotenv_values

PROJECT_ROOT = Path(__file__).resolve().parents[1]  # v2/
DEFAULT_ENV_FILE = PROJECT_ROOT / ".env"

WHISPER_MODELS = ("tiny", "base", "small", "medium", "large")
WHISPER_DEVICES = ("auto", "cpu", "cuda")
LANGUAGES = ("ja", "ko", "ar", "sr")
JAPANESE_SYSTEMS = ("hepburn", "kunrei", "passport")


class ConfigError(Exception):
    """A setting is missing or invalid. The message says which and how to fix it."""


@dataclass(frozen=True)
class Settings:
    genius_access_token: str
    whisper_model: str
    whisper_device: str
    default_language: str  # "" = auto-detect per line
    japanese_romanization: str
    output_dir: Path
    ffmpeg_path: str  # "" = use PATH
    align_width: int
    lang_confidence: float


def _choice(values, key, default, allowed, blank_ok=False):
    value = values.get(key, "").strip()
    if not value:
        return "" if blank_ok else default
    value = value.lower()
    if value not in allowed:
        raise ConfigError(f"{key}={value!r} is invalid. Use one of: {', '.join(allowed)}. Edit v2/.env.")
    return value


def load_settings(env_file=DEFAULT_ENV_FILE, environ=None):
    """Read settings from `env_file` (if it exists), then the process environment.

    Real environment variables win over the file. Pass env_file=None and an
    explicit `environ` dict in tests.
    """
    values = {}
    if env_file is not None and Path(env_file).is_file():
        values.update({k: v for k, v in dotenv_values(env_file, encoding="utf-8").items() if v is not None})
    values.update(os.environ if environ is None else environ)

    try:
        align_width = int(values.get("ALIGN_WIDTH", "").strip() or 75)
    except ValueError:
        raise ConfigError("ALIGN_WIDTH must be a whole number (display columns). Edit v2/.env.") from None
    if align_width < 10:
        raise ConfigError("ALIGN_WIDTH must be at least 10.")

    try:
        lang_confidence = float(values.get("LANG_CONFIDENCE", "").strip() or 0.25)
    except ValueError:
        raise ConfigError("LANG_CONFIDENCE must be a number between 0 and 1. Edit v2/.env.") from None
    if not 0 <= lang_confidence <= 1:
        raise ConfigError("LANG_CONFIDENCE must be between 0 and 1.")

    output_dir = Path(values.get("OUTPUT_DIR", "").strip() or "output")
    if not output_dir.is_absolute():
        output_dir = PROJECT_ROOT / output_dir

    return Settings(
        genius_access_token=values.get("GENIUS_ACCESS_TOKEN", "").strip(),
        whisper_model=_choice(values, "WHISPER_MODEL", "small", WHISPER_MODELS),
        whisper_device=_choice(values, "WHISPER_DEVICE", "auto", WHISPER_DEVICES),
        default_language=_choice(values, "DEFAULT_LANGUAGE", "", LANGUAGES, blank_ok=True),
        japanese_romanization=_choice(values, "JAPANESE_ROMANIZATION", "hepburn", JAPANESE_SYSTEMS),
        output_dir=output_dir,
        ffmpeg_path=values.get("FFMPEG_PATH", "").strip(),
        align_width=align_width,
        lang_confidence=lang_confidence,
    )


def require_genius_token(settings):
    """Return the Genius token or raise ConfigError. Call in Genius mode only."""
    if not settings.genius_access_token:
        raise ConfigError(
            "GENIUS_ACCESS_TOKEN is not set. Get a token at https://genius.com/api-clients "
            "and put it in v2/.env (Copy-Item .env.example .env)."
        )
    return settings.genius_access_token
