import argparse
import csv
import sys
import unicodedata
from pathlib import Path

import pykakasi

SYSTEMS = ("hepburn", "kunrei", "passport", "hira", "kana")
PARTICLES = {"は": "wa", "へ": "e", "を": "o"}

OPENING = "([{"

_kks = pykakasi.kakasi()


def romanize(text, system="hepburn", fix_particles=True):
    """Return `text` converted to the chosen romanization system."""
    if not text:
        return text
    text = unicodedata.normalize("NFKC", text)

    out = ""
    for token in _kks.convert(text):
        word = token[system]
        if fix_particles and system not in ("hira", "kana") and token["orig"] in PARTICLES:
            word = PARTICLES[token["orig"]]
        if not word:
            continue
        if system in ("hira", "kana"):
            out += word
            continue
        if out and not out[-1].isspace() and out[-1] not in OPENING and (word[0].isalnum() or word[0] in OPENING):
            out += " "
        out += word
    return out


def romanize_txt(src, dst, **opts):
    with open(src, encoding="utf-8-sig") as fin, open(dst, "w", encoding="utf-8", newline="") as fout:
        for line in fin:
            body = line.rstrip("\r\n")
            fout.write(romanize(body, **opts) + line[len(body):])


def romanize_csv(src, dst, **opts):
    with open(src, encoding="utf-8-sig", newline="") as fin, open(dst, "w", encoding="utf-8", newline="") as fout:
        writer = csv.writer(fout)
        for row in csv.reader(fin):
            writer.writerow([romanize(cell, **opts) for cell in row])


def main():
    parser = argparse.ArgumentParser(description="Romanize Japanese text in a .txt or .csv file.")
    parser.add_argument("input", type=Path, help="input .txt or .csv file (UTF-8)")
    parser.add_argument("-o", "--output", type=Path, help="output file (default: <input>_romanized.<ext>)")
    parser.add_argument("-s", "--system", choices=SYSTEMS, default="hepburn", help="romanization system (default: hepburn)")
    parser.add_argument("--literal-particles", action="store_true", help="keep は/へ/を as ha/he/wo instead of wa/e/o")
    args = parser.parse_args()

    if not args.input.is_file():
        sys.exit(f"Input file not found: {args.input}")

    output = args.output or args.input.with_name(f"{args.input.stem}_romanized{args.input.suffix}")
    opts = {"system": args.system, "fix_particles": not args.literal_particles}

    if args.input.suffix.lower() == ".csv":
        romanize_csv(args.input, output, **opts)
    else:
        romanize_txt(args.input, output, **opts)

    print(f"Romanized {args.input} -> {output}")


if __name__ == "__main__":
    main()
