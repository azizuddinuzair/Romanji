# Adapted from v1/romanization/korean_romanize.py (original author: Quang Duc Lam Nguyen)
#
# Changes from v1:
#   - v1 only exposes romanizing_Korean(), which loops over files in a hardcoded input/
#     folder and writes to output/, so it cannot be called on a string. This adapter keeps
#     the library calls it makes per line: Romanizer(line) then .romanize().

from korean_romanizer import Romanizer

LANG = "ko"


def romanize(line):
    line = Romanizer(line)
    return line.romanize()
