"""Command line: the only layer that prints or prompts.

    python -m romanji text <file> [--save]
"""

import argparse
import sys
from pathlib import Path

from .config import ConfigError, load_settings
from .output import default_txt_path, render_rows, save_txt
from .pipeline import EmptyLyricsError, run_text


def _build_parser():
    parser = argparse.ArgumentParser(prog="romanji", description="Romanize song lyrics, side by side.")
    sub = parser.add_subparsers(dest="command", required=True)

    text = sub.add_parser("text", help="romanize a lyrics file (UTF-8 .txt)")
    text.add_argument("file", type=Path, help="lyrics file")
    text.add_argument("--save", action="store_true", help="also write <name>_romanized.txt to OUTPUT_DIR")
    return parser


def main(argv=None, settings=None):
    # Windows consoles default to a legacy code page; force UTF-8 for CJK/Arabic.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")

    args = _build_parser().parse_args(argv)
    try:
        settings = settings or load_settings()
        if not args.file.is_file():
            print(f"Input file not found: {args.file}", file=sys.stderr)
            return 2
        _lines, rows = run_text(args.file, settings)
    except ConfigError as error:
        print(f"Configuration error: {error}", file=sys.stderr)
        return 2
    except EmptyLyricsError as error:
        print(str(error), file=sys.stderr)
        return 1
    except UnicodeDecodeError:
        print(f"{args.file} is not valid UTF-8. Re-save it as UTF-8.", file=sys.stderr)
        return 2

    print(render_rows(rows), end="")
    if args.save:
        saved = save_txt(rows, default_txt_path(args.file, settings.output_dir))
        print(f"\nSaved: {saved}", file=sys.stderr)
    return 0
