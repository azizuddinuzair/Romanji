"""Serbian: imports v1's romanize() (original author: Diego)."""

from ..v1_loader import load_v1_module

LANG = "sr"

_v1 = load_v1_module("romanization/serbian_romanize.py", "v1_serbian_romanize")


def romanize(line):
    return _v1.romanize(line)
