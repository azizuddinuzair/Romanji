# Adapted from v1/romanization/arabic_romanize.py (original author: Quang Duc Lam Nguyen)
#
# Changes from v1:
#   - v1 only exposes romanizing_Arabic(), which loops over files in a hardcoded input/
#     folder and writes to output/, so it cannot be called on a string. This adapter keeps
#     the library call it makes per line: arabic_to_latin(line).
# Note: arabic2latin does not add short vowels, so output is consonant-heavy.

from arabic2latin import arabic_to_latin

LANG = "ar"


def romanize(line):
    return arabic_to_latin(line)
