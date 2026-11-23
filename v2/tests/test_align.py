from wcwidth import wcswidth

from romanji.align import _split_by_width, align_lines, format_row, line_by_line


def test_ascii_rows_are_padded_to_spacing():
    rows = align_lines(["abc", "de"], ["x", "y"], spacing=10)
    assert rows == [("abc       ", "x"), ("de        ", "y")]
    assert format_row(rows[0]) == "abc        | x"


def test_every_left_column_has_exact_display_width_with_cjk_and_hangul():
    left = ["闇の中から新しい人生を始めよう", "Baby, 취해도 돼", "ララララ", "plain ascii", ""]
    right = ["yami no naka", "Baby, chwihaedo dwae", "rararara", "plain ascii", ""]
    rows = align_lines(left, right, spacing=30)
    assert len(rows) == 5
    for padded_left, _right in rows:
        assert wcswidth(padded_left) == 30


def test_double_width_text_wraps_by_display_width_not_characters():
    text = "あ" * 20  # 40 columns
    parts = _split_by_width(text, 10)
    assert parts == ["あ" * 5] * 4
    assert all(wcswidth(part) <= 10 for part in parts)


def test_wide_character_that_does_not_fit_moves_to_the_next_row():
    assert _split_by_width("あいう", 5) == ["あい", "う"]
    rows = align_lines(["あいう"], ["x"], spacing=5)
    assert rows == [("あい ", "x"), ("う   ", "")]
    assert all(wcswidth(left) == 5 for left, _ in rows)


def test_long_ascii_line_wraps_like_v1():
    rows = align_lines(["a" * 12], ["b" * 3], spacing=5)
    assert [left.rstrip() for left, _ in rows] == ["aaaaa", "aaaaa", "aa"]
    assert [right for _, right in rows] == ["bbb", "", ""]


def test_lists_of_different_length_are_padded_with_empty_lines():
    rows = align_lines(["one", "two", "three"], ["uno"], spacing=6)
    assert [right for _, right in rows] == ["uno", "", ""]
    rows = align_lines(["one"], ["uno", "dos"], spacing=6)
    assert [left.strip() for left, _ in rows] == ["one", ""]


def test_empty_inputs():
    assert align_lines([], [], spacing=10) == []
    assert align_lines([""], [""], spacing=4) == [("    ", "")]


def test_arabic_passes_through_unchanged():
    arabic = "أحبك كثيرا"
    rows = align_lines([arabic], ["ahbk kthyra"], spacing=20)
    assert rows[0][0].rstrip() == arabic
    assert wcswidth(rows[0][0]) == 20


def test_line_by_line_wrapper_reads_utf8_and_prints(tmp_path, capsys):
    left = tmp_path / "left.txt"
    right = tmp_path / "right.txt"
    left.write_text("闇の中\nBaby\n", encoding="utf-8")
    right.write_text("yami no\nBaby\n", encoding="utf-8")
    line_by_line(left, right, spacing=10)
    out = capsys.readouterr().out.splitlines()
    assert out == ["闇の中     | yami no", "Baby       | Baby"]
