# Adapted from v1/line_matching/line_by_line.py (original author: Vincent Mei)
#
# Changes from v1 (exactly three):
#   1. Both open() calls now pass encoding="utf-8" (v1 fails on Windows with CJK/Arabic).
#   2. Character-count chunking (line[k:k+spacing]) and padding (f"{sub1:<{spacing}}") are
#      replaced by display-width versions using wcwidth, in the helpers
#      _split_by_width() and _pad_to_width(). The main loop reads the same as before.
#   3. Reading and printing are separated: align_lines() takes two lists of lines and
#      returns rows; line_by_line(file1, file2) is kept as a wrapper with the original
#      signature (plus an optional `spacing`). The input() prompts moved to the CLI layer.
#      The wrapper still prints: it is the one documented exception to "no print() in
#      library code", kept for v1 compatibility. The pipeline does not use it.
# Known limitation: Arabic (right-to-left) text is passed through unchanged; no bidi handling.

from wcwidth import wcswidth, wcwidth


def _split_by_width(text, spacing):
    """Split `text` into chunks that are at most `spacing` display columns wide."""
    parts = []
    current = ""
    used = 0
    for char in text:
        width = max(wcwidth(char), 0)
        if current and used + width > spacing:
            parts.append(current)
            current = ""
            used = 0
        current += char
        used += width
    if current:
        parts.append(current)
    return parts


def _pad_to_width(text, spacing):
    """Pad `text` with spaces up to `spacing` display columns."""
    return text + " " * max(spacing - max(wcswidth(text), 0), 0)


def align_lines(list1, list2, spacing=75):
    """Pair two lists of lines. Returns a list of (left, right) rows.

    Each pair is chunked to `spacing` display columns; `left` is padded to exactly
    `spacing` columns so the separator lines up. The longer chunk list decides how
    many rows a pair takes.
    """
    rows = []
    total_lines = max(len(list1), len(list2))

    for i in range(total_lines):
        line1 = list1[i] if i < len(list1) else ""
        line2 = list2[i] if i < len(list2) else ""

        parts1 = _split_by_width(line1, spacing) or [""]

        parts2 = _split_by_width(line2, spacing) or [""]

        sub_rows = max(len(parts1), len(parts2))
        for j in range(sub_rows):
            sub1 = parts1[j] if j < len(parts1) else ""
            sub2 = parts2[j] if j < len(parts2) else ""
            rows.append((_pad_to_width(sub1, spacing), sub2))
    return rows


def format_row(row):
    """Render one (left, right) row as 'left | right' (the v1 output format)."""
    left, right = row
    return f"{left} | {right}"


def line_by_line(file1, file2, spacing=75):
    """v1 signature kept: print two files side by side."""
    with open(file1, "r", encoding="utf-8") as f:
        list1 = [line.rstrip("\n") for line in f]

    with open(file2, "r", encoding="utf-8") as f:
        list2 = [line.rstrip("\n") for line in f]

    for row in align_lines(list1, list2, spacing):
        print(format_row(row))
