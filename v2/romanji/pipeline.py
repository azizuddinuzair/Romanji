"""Pipeline: source -> clean -> detect -> romanize -> align. No printing, no prompts."""

from dataclasses import replace

from . import romanizers
from .align import align_lines
from .clean import clean_lines
from .detect import detect_lines
from .sources.text import read_text_lines


class EmptyLyricsError(Exception):
    """No lyric lines are left after cleaning."""


def process_lines(lines, settings):
    """clean -> detect -> romanize. Returns lines with `lang` and `romanized` set."""
    lines = clean_lines(lines)
    if not lines:
        raise EmptyLyricsError("No lyric lines found after cleaning.")
    lines = detect_lines(lines, settings.default_language, settings.lang_confidence)
    romanizers.configure(settings.japanese_romanization)
    return [replace(line, romanized=romanizers.romanize(line.text, line.lang)) for line in lines]


def to_rows(lines, settings):
    """align original (left) and romanized (right) text."""
    left = [line.text for line in lines]
    right = [line.romanized if line.romanized is not None else line.text for line in lines]
    return align_lines(left, right, settings.align_width)


def run_text(path, settings):
    """Text path: lyrics file -> (processed lines, aligned rows)."""
    lines = process_lines(read_text_lines(path), settings)
    return lines, to_rows(lines, settings)
