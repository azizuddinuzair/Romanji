from romanji.clean import clean_lines
from romanji.models import Line
from romanji.sources.text import read_text_lines


def texts(strings):
    return [line.text for line in clean_lines([Line(text=s) for s in strings])]


def test_blank_lines_and_whitespace_are_dropped_or_stripped():
    assert texts(["  hello  ", "", "   ", "world"]) == ["hello", "world"]


def test_original_three_prefixes_are_dropped():
    assert texts(["[Verse 1]", "[Chorus]", "[Bridge]", "keep me"]) == ["keep me"]


def test_any_bracketed_tag_is_dropped():
    tags = ["[Intro]", "[Pre-Chorus]", "[序奏]", "[ヴァース 1]", "[Verse 2: Someone]", "[Outro]"]
    assert texts(tags + ["keep me"]) == ["keep me"]


def test_tag_wrapped_in_punctuation_is_dropped():
    assert texts(['--[神聖かまってちゃん「僕の戦争」日本語訳]', "keep me"]) == ["keep me"]


def test_line_that_merely_contains_brackets_is_kept():
    assert texts(["[a] real lyric [b]", "hello [yeah]", "(oh) yeah"]) == [
        "[a] real lyric [b]",
        "hello [yeah]",
        "(oh) yeah",
    ]


def test_genius_header_title_line_is_dropped():
    assert texts(["Song Title Lyrics", "first lyric", "second lyric"]) == ["first lyric", "second lyric"]


def test_genius_header_with_fused_contributors_is_dropped():
    assert texts(["12 ContributorsYoru ni Kakeru Lyrics", "first lyric"]) == ["first lyric"]


def test_contributors_line_is_dropped():
    assert texts(["Song Lyrics", "3 Contributors", "first lyric"]) == ["first lyric"]


def test_lyrics_word_at_end_of_a_later_line_is_kept():
    assert texts(["first lyric", "I write these Lyrics"]) == ["first lyric", "I write these Lyrics"]


def test_trailing_embed_is_stripped_from_the_last_line():
    assert texts(["first lyric", "last lyric123Embed"]) == ["first lyric", "last lyric"]
    assert texts(["first lyric", "last lyricEmbed"]) == ["first lyric", "last lyric"]


def test_embed_alone_on_last_line_is_dropped():
    assert texts(["first lyric", "42Embed"]) == ["first lyric"]


def test_embed_in_the_middle_is_untouched():
    assert texts(["I said Embed", "last lyric"]) == ["I said Embed", "last lyric"]


def test_empty_input():
    assert clean_lines([]) == []
    assert texts(["", "  "]) == []


def test_timestamps_are_preserved():
    cleaned = clean_lines([Line(text="[Intro]", start=0.0), Line(text="hi", start=1.5, end=2.5)])
    assert cleaned == [Line(text="hi", start=1.5, end=2.5)]


def test_japanese_test_file_header_and_tags(japanese_file):
    raw = read_text_lines(japanese_file)
    assert raw[0].text.startswith("--[")  # guard: the junk lines are really in the file
    assert any(line.text == "[序奏]" for line in raw)

    cleaned = [line.text for line in clean_lines(raw)]
    assert cleaned[0] == "ララララ"
    assert not any(text.startswith("--[") or "日本語訳]" in text for text in cleaned)
    assert not any(text.startswith("[") for text in cleaned)
    assert "[序奏]" not in cleaned
    assert "[ヴァース 1]" not in cleaned
    assert "闇の中から新しい人生を始めよう" in cleaned


def test_korean_test_file_title_line(korean_file):
    raw = read_text_lines(korean_file)
    assert raw[0].text.startswith("[") and raw[0].text.endswith("]")
    cleaned = [line.text for line in clean_lines(raw)]
    assert cleaned[0] == "내 피, 땀, 눈물, 내 마지막 춤을"
