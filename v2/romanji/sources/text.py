"""Text source: a UTF-8 lyrics file -> list[Line]."""

from pathlib import Path

from ..models import Line


def read_text_lines(path):
    """Read a lyrics file (UTF-8, BOM allowed). Raises FileNotFoundError."""
    text = Path(path).read_text(encoding="utf-8-sig")
    return [Line(text=raw) for raw in text.splitlines()]
