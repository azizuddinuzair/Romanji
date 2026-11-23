"""Romanizer registry. One interface for every language:

    romanize(line: str, lang: str) -> str

To add a language: create romanizers/<code>.py with `LANG` and `romanize(line)`,
then add it to REGISTRY below.
"""

import unicodedata

from . import ar, ja, ko, sr

REGISTRY = {module.LANG: module for module in (ja, ko, ar, sr)}


def configure(japanese_system="hepburn"):
    """Apply settings that a romanizer needs (called once by the pipeline)."""
    ja.configure(japanese_system)


def _has_non_latin_letter(line):
    return any(ch.isalpha() and not unicodedata.name(ch, "").startswith("LATIN") for ch in line)


def romanize(line, lang):
    """Romanize one line. Unknown/und languages and Latin-only lines are returned unchanged.

    Serbian is the exception: Latin-script Serbian is still processed (v1 maps č/ć/š/ž/đ).
    """
    module = REGISTRY.get(lang)
    if module is None or not line.strip():
        return line
    if lang != "sr" and not _has_non_latin_letter(line):
        return line
    return module.romanize(line)
