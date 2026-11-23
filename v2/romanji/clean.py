# Adapted from v1/lyric_cleaner/lyric-cleaner.py (original author: Abhi Seela)
#
# Changes from v1:
#   - Takes and returns list[Line] instead of reading Genius output inside lyricClean()
#     (no input(), no file write, no Genius client here; sources/genius.py will own that).
#   - Kept: the line loop, line.strip(), the empty-line check and the three
#     startswith checks ("[Verse", "[Chorus", "[Bridge").
#   - Added: drop any line that is entirely a bracketed tag ([Intro], [序奏], [Pre-Chorus],
#     --[...日本語訳]) via TAG_RE, because Genius uses many more section names than three.
#   - Added: drop Genius header/footer junk: "N Contributors", the first-line
#     "...Lyrics" title (also when fused after "N Contributors"), and a trailing
#     "Embed" / "123Embed" on the last line.
#   - snake_case names (lyricClean -> clean_lines, tokenizedSong -> cleaned).

import re
from dataclasses import replace

from .models import Line

# Whole line is one [bracketed tag], optionally wrapped in punctuation such as "--".
# [^\]]* (not .*) so "[a] real lyric [b]" is NOT dropped.
TAG_RE = re.compile(r"\W*\[[^\]]*\]\W*")
CONTRIBUTORS_RE = re.compile(r"\d+\s*Contributors?", re.IGNORECASE)
EMBED_RE = re.compile(r"\d*Embed$")


def _is_header_junk(text):
    """First non-blank line: 'N ContributorsSong Title Lyrics' / 'Song Title Lyrics'."""
    rest = CONTRIBUTORS_RE.sub("", text, count=1) if CONTRIBUTORS_RE.match(text) else text
    rest = rest.strip()
    return rest == "" or rest.endswith("Lyrics")


def clean_lines(lines):
    """Return `lines` without blanks, section tags and Genius header/footer junk."""
    texts = [line.text.strip() for line in lines]
    non_blank = [i for i, text in enumerate(texts) if text != ""]
    first = non_blank[0] if non_blank else None
    last = non_blank[-1] if non_blank else None

    cleaned = []
    for i, original in enumerate(lines):
        text = texts[i]

        if i == last:
            text = EMBED_RE.sub("", text).strip()
        if i == first and _is_header_junk(text):
            continue
        if CONTRIBUTORS_RE.fullmatch(text):
            continue

        if (
            text != ""
            and not text.startswith("[Verse")
            and not text.startswith("[Chorus")
            and not text.startswith("[Bridge")
            and not TAG_RE.fullmatch(text)
        ):
            cleaned.append(replace(original, text=text))
    return cleaned
