# Adapted from v1/lang_detection/sample.py (original author: JasmithaK)
#
# Changes from v1:
#   - Works on one line of text at a time instead of a whole file (v1's detect_languages()
#     takes a file path and prints errors, so it cannot be called per line).
#   - Kept: detect_langs(), the `prob >= confidence_threshold` filter, and the catch of
#     LangDetectException. The threshold now comes from LANG_CONFIDENCE (v1 default 0.25).
#   - Added: Unicode-script rules first, because langdetect has no "sr" profile and is
#     unreliable on short lines; the mapping table below; DetectorFactory.seed = 0
#     (langdetect is otherwise nondeterministic).

import unicodedata
from collections import Counter
from dataclasses import replace

from langdetect import DetectorFactory, LangDetectException, detect_langs

DetectorFactory.seed = 0

UNDETERMINED = "und"

# ----------------------------------------------------------------------------
# MAPPING TABLE: the only place that decides what a detection result means.
# ----------------------------------------------------------------------------
# 1. Script -> language. Checked first; the script with the most characters wins.
#    (name, unicode ranges, language)
SCRIPT_TO_LANG = (
    ("kana", ((0x3040, 0x30FF), (0x31F0, 0x31FF), (0xFF66, 0xFF9F)), "ja"),
    ("hangul", ((0x1100, 0x11FF), (0x3130, 0x318F), (0xAC00, 0xD7AF)), "ko"),
    ("arabic", ((0x0600, 0x06FF), (0x0750, 0x077F), (0x08A0, 0x08FF), (0xFB50, 0xFDFF), (0xFE70, 0xFEFF)), "ar"),
    ("cyrillic", ((0x0400, 0x04FF),), "sr"),  # only Cyrillic language we support
)
# 2. Han characters alone say nothing (ja or zh): the line inherits the file-level language.
HAN_RANGES = ((0x3400, 0x4DBF), (0x4E00, 0x9FFF))
# 3. Latin-script lines: langdetect code -> language. Anything not listed (en, es, ...) -> und.
LANGDETECT_TO_LANG = {"ja": "ja", "ko": "ko", "ar": "ar", "hr": "sr", "sl": "sr", "bs": "sr"}
# 4. Whisper auto-detect code -> language (used by audio mode).
WHISPER_TO_LANG = {"ja": "ja", "ko": "ko", "ar": "ar", "sr": "sr", "hr": "sr", "bs": "sr"}
# ----------------------------------------------------------------------------


def _in_ranges(code, ranges):
    return any(low <= code <= high for low, high in ranges)


def _script_counts(text):
    """Count characters per script ("han", "latin" and the SCRIPT_TO_LANG names)."""
    counts = Counter()
    for ch in text:
        code = ord(ch)
        for name, ranges, _lang in SCRIPT_TO_LANG:
            if _in_ranges(code, ranges):
                counts[name] += 1
                break
        else:
            if _in_ranges(code, HAN_RANGES):
                counts["han"] += 1
            elif ch.isalpha() and unicodedata.name(ch, "").startswith("LATIN"):
                counts["latin"] += 1
    return counts


def _detect_latin(text, confidence_threshold):
    """langdetect on Latin text, mapped through LANGDETECT_TO_LANG (v1's filter kept)."""
    try:
        detected_langs = detect_langs(text)
    except LangDetectException:
        return UNDETERMINED
    filtered_langs = [lang for lang in detected_langs if lang.prob >= confidence_threshold]
    for lang in filtered_langs:
        if lang.lang in LANGDETECT_TO_LANG:
            return LANGDETECT_TO_LANG[lang.lang]
    return UNDETERMINED


def detect_line(text, confidence_threshold=0.25):
    """Return ja | ko | ar | sr | und, or "han" for a line of only Han characters."""
    counts = _script_counts(text)
    certain = [(counts[name], lang) for name, _ranges, lang in SCRIPT_TO_LANG if counts[name]]
    if certain:
        return max(certain, key=lambda pair: pair[0])[1]
    if counts["han"]:
        return "han"
    if counts["latin"]:
        return _detect_latin(text, confidence_threshold)
    return UNDETERMINED


def file_level_language(per_line, lines, confidence_threshold=0.25):
    """Language of the whole file, used for Han-only lines.

    Majority of the script-certain lines (ja/ko/ar/sr); if there are none, langdetect
    on the joined text mapped through the table; otherwise und.
    """
    votes = Counter(lang for lang in per_line if lang in LANGDETECT_TO_LANG.values() or lang == "sr")
    if votes:
        return votes.most_common(1)[0][0]
    joined = "\n".join(line.text for line in lines)
    if joined.strip():
        try:
            for lang in detect_langs(joined):
                if lang.prob >= confidence_threshold and lang.lang in LANGDETECT_TO_LANG:
                    return LANGDETECT_TO_LANG[lang.lang]
        except LangDetectException:
            pass
    return UNDETERMINED


def detect_lines(lines, default_language="", confidence_threshold=0.25):
    """Set Line.lang on every line. `default_language` (ja|ko|ar|sr) overrides detection."""
    if default_language:
        return [replace(line, lang=default_language) for line in lines]

    per_line = [detect_line(line.text, confidence_threshold) for line in lines]
    if "han" in per_line:
        fallback = file_level_language([lang for lang in per_line if lang != "han"], lines, confidence_threshold)
        per_line = [fallback if lang == "han" else lang for lang in per_line]
    return [replace(line, lang=lang) for line, lang in zip(lines, per_line)]
