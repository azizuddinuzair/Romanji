from collections import Counter

import pytest

from romanji import detect
from romanji.clean import clean_lines
from romanji.detect import detect_line, detect_lines
from romanji.models import Line
from romanji.sources.text import read_text_lines


def langs(strings, **kwargs):
    return [line.lang for line in detect_lines([Line(text=s) for s in strings], **kwargs)]


@pytest.mark.parametrize(
    "text, expected",
    [
        ("闇の中から新しい人生を始めよう", "ja"),
        ("ララララ", "ja"),
        ("내 피, 땀, 눈물, 내 마지막 춤을", "ko"),
        ("أحبك كثيرا", "ar"),
        ("Ја волим тебе", "sr"),  # Cyrillic -> sr
        ("Ne znam šta da radim bez tebe", "sr"),  # Latin Serbian (langdetect says hr/sl/bs)
        ("Baby, I'm falling", "und"),  # English -> und
        ("♪ ♪", "und"),
        ("123", "und"),
        ("", "und"),
    ],
)
def test_single_lines(text, expected):
    assert detect_line(text) == expected


def test_mixed_lines_follow_the_dominant_script():
    assert detect_line("Baby, 취해도 돼, 이제 널 들이켜") == "ko"
    assert detect_line("Baby, 愛してる") == "ja"


def test_mixed_language_song_is_detected_per_line():
    assert langs(["I love you so", "君を愛してる", "사랑해", "Ја волим тебе"]) == ["und", "ja", "ko", "sr"]


def test_serbian_in_both_scripts():
    assert langs(["Ја волим тебе", "Ne znam šta da radim bez tebe"]) == ["sr", "sr"]


def test_han_only_line_inherits_file_majority():
    assert langs(["君を愛してる", "私は元気です", "愛"]) == ["ja", "ja", "ja"]
    assert langs(["사랑해 너를", "내 마음", "愛"]) == ["ko", "ko", "ko"]


class _Guess:
    def __init__(self, lang, prob):
        self.lang, self.prob = lang, prob


def test_han_only_file_falls_back_to_langdetect_through_the_table(monkeypatch):
    monkeypatch.setattr(detect, "detect_langs", lambda text: [_Guess("zh-cn", 0.99)])
    assert langs(["愛", "夢"]) == ["und", "und"]  # Chinese is not supported
    monkeypatch.setattr(detect, "detect_langs", lambda text: [_Guess("ja", 0.9)])
    assert langs(["愛", "夢"]) == ["ja", "ja"]
    monkeypatch.setattr(detect, "detect_langs", lambda text: [_Guess("ja", 0.1)])
    assert langs(["愛", "夢"]) == ["und", "und"]  # below the confidence threshold


def test_default_language_overrides_detection():
    assert langs(["Baby", "君を愛してる"], default_language="ko") == ["ko", "ko"]


def test_confidence_threshold_is_applied():
    # "oh yeah" is ~0.71 en: below a 0.99 threshold no language qualifies -> und either way
    assert detect_line("oh yeah", confidence_threshold=0.99) == "und"


def test_detection_is_deterministic():
    runs = {tuple(langs(["Volim te mnogo", "La la la", "oh yeah"])) for _ in range(5)}
    assert len(runs) == 1


def test_mapping_table():
    assert detect.LANGDETECT_TO_LANG["hr"] == "sr"
    assert detect.LANGDETECT_TO_LANG["sl"] == "sr"
    assert detect.LANGDETECT_TO_LANG["bs"] == "sr"
    assert "en" not in detect.LANGDETECT_TO_LANG
    assert detect.WHISPER_TO_LANG["hr"] == "sr"
    assert detect.WHISPER_TO_LANG["bs"] == "sr"


def test_japanese_test_file_is_mostly_ja(japanese_file):
    lines = detect_lines(clean_lines(read_text_lines(japanese_file)))
    counts = Counter(line.lang for line in lines)
    assert counts["ja"] == len(lines)


def test_korean_test_file_is_ko(korean_file):
    lines = detect_lines(clean_lines(read_text_lines(korean_file)))
    assert Counter(line.lang for line in lines)["ko"] == len(lines)
