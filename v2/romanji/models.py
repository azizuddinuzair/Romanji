"""Data passed between pipeline stages."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Line:
    """One lyric line.

    text       original text
    start/end  seconds, only set in audio mode
    lang       ja | ko | ar | sr | und (set by detect)
    romanized  set by romanize
    Stages return new Line objects (dataclasses.replace); they never mutate.
    """

    text: str
    start: float | None = None
    end: float | None = None
    lang: str | None = None
    romanized: str | None = None
