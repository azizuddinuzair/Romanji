import argparse
import sys
import unicodedata
from pathlib import Path

CYRILLIC_TO_LATIN = {
    "а": "a",  "б": "b",  "в": "v",  "г": "g",  "д": "d",
    "ђ": "đ",  "е": "e",  "ж": "ž",  "з": "z",  "и": "i",
    "ј": "j",  "к": "k",  "л": "l",  "љ": "lj", "м": "m",
    "н": "n",  "њ": "nj", "о": "o",  "п": "p",  "р": "r",
    "с": "s",  "т": "t",  "ћ": "ć",  "у": "u",  "ф": "f",
    "х": "h",  "ц": "c",  "ч": "č",  "џ": "dž", "ш": "š",
}

SPECIAL_TO_PLAIN = {"č": "ch", "ć": "ch", "š": "sh", "ž": "zh", "đ": "dj"}

def convert_letters(text, table):
    out = ""
    for letter in text:
        small = letter.lower()
        if small in table:
            new = table[small]
            if letter != small:
                new = new.capitalize()
            out += new
        else:
            out += letter
    return out

def romanize(text):
    text = unicodedata.normalize("NFC", text)
    text = convert_letters(text, CYRILLIC_TO_LATIN)
    text = convert_letters(text, SPECIAL_TO_PLAIN)
    return text


def romanize_file(src, dst):
    with open(src, encoding="utf-8") as fin, open(dst, "w", encoding="utf-8") as fout:
        for line in fin:
            fout.write(romanize(line))


def main():
    parser = argparse.ArgumentParser(description="Romanize Serbian text (Cyrillic or Latin) in a .txt file.")
    parser.add_argument("input", type=Path, help="input .txt file (UTF-8)")
    args = parser.parse_args()

    if not args.input.is_file():
        sys.exit(f"Input file not found: {args.input}")

    output = args.input.with_name(f"{args.input.stem}_romanized{args.input.suffix}")
    romanize_file(args.input, output)
    print(f"Romanized {args.input} -> {output}")


if __name__ == "__main__":
    main()

