
from pathlib import Path
from korean_romanizer import Romanizer
import re

# Get the directory containing this Python file.
folder = Path(__file__).parent

input_file = folder / "lyrics.txt"
output_file = folder / "output.txt"


def romanize_word(word):
    """Romanize a Korean word using the Revised Romanization."""
    return Romanizer(word).romanize()


def process_line(line):
    # Keep whitespace and punctuation; process only one word at a time
    tokens = re.findall(r"\s+|[가-힣]+|[^가-힣\s]+", line)
    result = []

    for token in tokens:
        if re.fullmatch(r"[가-힣]+", token):
            romanized = romanize_word(token)

            # Add hyphens between original Hangul syllables.
            # This classification is approximate and does not guarantee accuracy (I'm still working on)
            #for every instance of sound change in Korean.
            syllables = list(token)
            if len(syllables) == 1:
                result.append(romanized)
            else:
                # Romanize each syllables to create hyphens '-'.
                parts = [
                    romanize_word(syllable)
                    for syllable in syllables
                ]
                result.append("-".join(parts))
        else:
            result.append(token)

    return "".join(result)


def main():
    if not input_file.exists():
        print(f"Cannot find the file: {input_file}")
        return

    text = input_file.read_text(encoding="utf-8-sig")

    output_lines = [
        process_line(line)
        for line in text.splitlines()
    ]

    output_file.write_text(
        "\n".join(output_lines),
        encoding="utf-8"
    )

    print(f"Process complete: {output_file}")


if __name__ == "__main__":
    main()
