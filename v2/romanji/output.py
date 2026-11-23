"""Output: render aligned rows as text and save a .txt. Printing is done by cli.py."""

from pathlib import Path

from .align import format_row


def render_rows(rows):
    """Join rows into the text shown in the terminal and saved to .txt."""
    return "\n".join(format_row(row).rstrip() for row in rows) + "\n"


def default_txt_path(input_path, output_dir):
    """<output_dir>/<input stem>_romanized.txt"""
    return Path(output_dir) / f"{Path(input_path).stem}_romanized.txt"


def save_txt(rows, path):
    """Write the side-by-side text to `path` (UTF-8), creating folders. Returns the path."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_rows(rows), encoding="utf-8")
    return path
