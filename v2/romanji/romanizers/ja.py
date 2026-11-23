"""Japanese: imports v1's romanize() (original author: Pprajapati7964)."""

from ..v1_loader import load_v1_module

LANG = "ja"

_v1 = load_v1_module("romanization/romanization.py", "v1_romanization")
_system = "hepburn"


def configure(system):
    """Set the romanization system (hepburn | kunrei | passport) from JAPANESE_ROMANIZATION."""
    global _system
    _system = system


def romanize(line):
    return _v1.romanize(line, system=_system)
