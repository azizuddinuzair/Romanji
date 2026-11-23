from dataclasses import replace

import pytest
from wcwidth import wcswidth

from romanji.cli import main
from romanji.models import Line
from romanji.output import default_txt_path, render_rows, save_txt
from romanji.pipeline import EmptyLyricsError, process_lines, run_text, to_rows
from romanji.sources.text import read_text_lines


def test_text_source_reads_utf8_with_bom(tmp_path):
    path = tmp_path / "song.txt"
    path.write_bytes("﻿闇の中\r\nBaby\r\n".encode("utf-8"))
    assert [line.text for line in read_text_lines(path)] == ["闇の中", "Baby"]


def test_japanese_file_end_to_end(japanese_file, settings):
    lines, rows = run_text(japanese_file, settings)
    assert len(lines) == 25  # 35 raw lines minus 10 blank, tag and title lines
    assert rows[0][0].rstrip() == "ララララ"
    assert rows[0][1] == "rararara"
    assert rows[1][1] == "yami no naka kara atarashii jinsei o hajime you"
    assert all(wcswidth(left) == settings.align_width for left, _ in rows)


def test_korean_file_end_to_end(korean_file, settings):
    lines, rows = run_text(korean_file, settings)
    assert rows[0] == (rows[0][0], "nae pi, ttam, nunmul, nae majimak chumeul")
    assert rows[0][0].rstrip() == "내 피, 땀, 눈물, 내 마지막 춤을"
    mixed = [right for left, right in rows if left.startswith("Baby")]
    assert mixed == ["Baby, chwihaedo dwae, ije neol deurikyeo"]
    assert all(wcswidth(left) == settings.align_width for left, _ in rows)


def test_mixed_language_song(settings):
    lines = process_lines(
        [Line("[Intro]"), Line("I love you"), Line("君を愛してる"), Line("사랑해"), Line("Ја волим тебе")], settings
    )
    assert [line.lang for line in lines] == ["und", "ja", "ko", "sr"]
    assert lines[0].romanized == "I love you"  # Latin line left as it is
    assert lines[3].romanized == "Ja volim tebe"


def test_default_language_setting(settings):
    forced = replace(settings, default_language="ko")
    lines = process_lines([Line("Baby"), Line("사랑해")], forced)
    assert [line.lang for line in lines] == ["ko", "ko"]
    assert lines[0].romanized == "Baby"


def test_japanese_romanization_setting(settings):
    kunrei = replace(settings, japanese_romanization="kunrei")
    [line] = process_lines([Line("つづく")], kunrei)
    assert line.romanized == "tuzuku"  # hepburn gives "tsuzuku"


def test_only_junk_raises(settings):
    with pytest.raises(EmptyLyricsError):
        process_lines([Line("[Intro]"), Line(""), Line("[Outro]")], settings)


def test_to_rows_falls_back_to_original_when_not_romanized(settings):
    assert to_rows([Line("abc")], replace(settings, align_width=10)) == [("abc       ", "abc")]


def test_output_render_and_save(tmp_path):
    rows = [("あい   ", "ai"), ("b      ", "b")]
    assert render_rows(rows) == "あい    | ai\nb       | b\n"
    path = save_txt(rows, tmp_path / "nested" / "out.txt")
    assert path.read_text(encoding="utf-8") == render_rows(rows)
    assert default_txt_path("some/dir/song.txt", tmp_path) == tmp_path / "song_romanized.txt"


def test_cli_prints_and_saves_utf8(tmp_path, settings, japanese_file, capfd):
    settings = replace(settings, output_dir=tmp_path / "out")
    assert main(["text", str(japanese_file), "--save"], settings=settings) == 0
    printed = capfd.readouterr().out
    assert "yami no naka kara atarashii jinsei o hajime you" in printed
    saved = (tmp_path / "out" / "japaneseTestFile_romanized.txt").read_text(encoding="utf-8")
    assert saved == printed


def test_cli_missing_file(tmp_path, settings, capsys):
    assert main(["text", str(tmp_path / "nope.txt")], settings=settings) == 2
    assert "not found" in capsys.readouterr().err


def test_cli_empty_lyrics(tmp_path, settings, capsys):
    path = tmp_path / "tags.txt"
    path.write_text("[Intro]\n\n[Outro]\n", encoding="utf-8")
    assert main(["text", str(path)], settings=settings) == 1
    assert "No lyric lines" in capsys.readouterr().err


def test_cli_non_utf8_file(tmp_path, settings, capsys):
    path = tmp_path / "latin1.txt"
    path.write_bytes("caf\xe9\n".encode("latin-1"))
    assert main(["text", str(path)], settings=settings) == 2
    assert "UTF-8" in capsys.readouterr().err
