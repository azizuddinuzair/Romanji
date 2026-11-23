# Romanji v2 — instructions for agents

Romanji takes a song (lyrics file, Genius title+artist, or audio file), romanizes the lyrics and prints original and romanized text side by side. Languages: Japanese (ja), Korean (ko), Arabic (ar), Serbian (sr).

**Status:** Milestone 1 (text path: `python -m romanji text <file> [--save]`) is built and tested. Genius mode (`sources/genius.py`) and audio mode (`sources/audio.py`, `--lrc`) are not built yet. Check the tree before assuming a file exists.

Contract notes from Milestone 1:
- `romanizers.romanize(line, lang)` keeps its signature; per-run settings go through `romanizers.configure(japanese_system)`, which the pipeline calls from `Settings`.
- `align.line_by_line()` still prints (v1 compatibility, the one documented exception to "no `print()`"); the pipeline uses `align_lines()` + `output.render_rows()`, and only `cli.py` prints.
- Han-only lines take the file-level language: majority of the script-certain lines, else `langdetect` on the joined text through the table, else `und`.
- `romanji/__main__.py` and package `__init__.py` files exist for `python -m romanji`.

## Rules about v1 (a team project — read first)
- `v1/` is **read-only**. Never edit, move, rename, reformat or delete anything in it, including its broken test paths. Report v1 problems to the user instead of fixing them.
- **Import v1 code; don't rewrite it.** Load it by file path through `romanji/v1_loader.py` (v1 has no packages and `lyric-cleaner.py` has a hyphen).
- If a v1 script can't be imported as is, write a thin adapter in v2 that calls the original logic.
- Copy only when unavoidable. Keep original function names, comments and structure, change as little as possible, and start the file with:
  `# Adapted from v1/<path> (original author: <name>)`
  followed by a `Changes from v1` comment block listing every change and why.
- **Ask before replacing a teammate's implementation**, and ask which style to follow if v1 modules conflict. New v2 code uses snake_case, docstrings and `pathlib`.
- Keep attribution. Do not remove author headers.

### Module owners (from git history)
| v1 module | Owner |
|---|---|
| lang_detection/sample.py | JasmithaK |
| line_matching/line_by_line.py | Vincent Mei |
| lyric_cleaner/ | Abhi Seela |
| romanization/romanization.py (ja) | Pprajapati7964 |
| romanization/serbian_romanize.py | Diego |
| romanization/korean_romanize.py, arabic_romanize.py | Quang Duc Lam Nguyen |
| speech_to_text_test/ (Whisper GUI, mic test) | ComicShadow |
| scaffolding/stubs | Uzair Azizuddin |

Thanh Dat Vo edited romanization.py on the unmerged `Korean_Romanize` branch. That is **pending a team decision**; v2 imports main's version until then. Names are as they appear in git; some are GitHub handles.

## Layout
```
v2/
  CLAUDE.md README.md .env.example .python-version
  requirements.txt  requirements-audio.txt  requirements-dev.txt
  romanji/
    config.py      only place that reads .env
    models.py      Line(text, start, end, lang, romanized)
    v1_loader.py   import v1 modules by file path
    sources/       text.py  genius.py  audio.py
    clean.py  detect.py  align.py  output.py  pipeline.py  cli.py
    romanizers/    __init__.py (registry)  ja.py  ko.py  ar.py  sr.py
  tests/
```

## Setup and run (Windows + PowerShell)
Python **3.12** for everything in v2 (Whisper's dependencies — torch, numba — don't support 3.14; `python-ver.txt` says 3.12.10). The repo-root `.python-version` says 3.14; leave it alone, v2 has its own. The environment is built with **uv**, which downloads a managed 3.12 itself, so don't install Python system-wide.
```powershell
cd v2
py -m uv --version                     # if this fails: py -m pip install --user uv
py -m uv venv --python 3.12 --seed     # creates v2\.venv (gitignored); --seed adds pip
.\.venv\Scripts\Activate.ps1           # may need: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
pip install -r requirements-dev.txt    # core + pytest. Audio mode: also -r requirements-audio.txt
Copy-Item .env.example .env            # then fill in GENIUS_ACCESS_TOKEN (Genius mode only)
python -m romanji text song.txt [--save]
python -m romanji genius "<song>" "<artist>"     # not built yet
python -m romanji audio song.mp3 --lrc --save    # not built yet
winget install Gyan.FFmpeg             # audio mode only; or set FFMPEG_PATH
```
Windows: console output must be UTF-8 (`cli.py` reconfigures stdout; Windows Terminal handles CJK width, legacy conhost may not).

## Pipeline: source → clean → detect → romanize → align → output
`Line` is the unit passed between stages. Stages never print or prompt.
1. **Source** → `list[Line]`. Text: UTF-8 file. Genius: song+artist → lines. Audio: Whisper segments, one `Line` per segment with `start`/`end`.
2. **Clean** `list[Line]` → `list[Line]`. Drop blank lines; keep the three v1 prefix checks (`[Verse`, `[Chorus`, `[Bridge`); drop any line matching `re.fullmatch(r"\W*\[[^\]]*\]\W*", line)` (`[Intro]`, `[序奏]`, `--[…日本語訳]`); drop `N Contributors`, the first-line `…Lyrics` title; strip a trailing `\d*Embed`.
3. **Detect** → sets `Line.lang` in `{ja, ko, ar, sr, und}` **per line**. `und` passes through untouched. `DEFAULT_LANGUAGE` overrides everything.
4. **Romanize** `romanize(line: str, lang: str) -> str`. Latin-script and `und` lines come back unchanged.
5. **Align** `align_lines(left, right, spacing) -> list[tuple[str, str]]`, pure, using display width (`wcwidth`). `line_by_line(file1, file2)` keeps its v1 signature as a wrapper.
6. **Output** terminal, `.txt` in `OUTPUT_DIR`, and `.lrc` with `--lrc` (audio mode).

## Conventions
- UTF-8 on **every** `open()`/`read_text()`/`write_text()` (`encoding="utf-8"`; `utf-8-sig` for reading user files). v1's `line_by_line.py` fails on Windows without it.
- No hardcoded paths. Resolve from `__file__` or `Settings`, never from the current directory.
- No `input()` or `print()` in library code; only `cli.py` prompts and prints.
- Settings are read only in `romanji/config.py` (python-dotenv, path from `__file__`). A missing `GENIUS_ACCESS_TOKEN` fails only in Genius mode; ffmpeg is checked only in audio mode.
- Every romanizer sits behind `romanize(line, lang) -> str`.
- **Never commit `.env`. Never hardcode a token. Never print `.env` contents. Add every new setting to `.env.example` in the same change.**

## Add a language
1. Create `romanji/romanizers/<code>.py` with `LANG = "<code>"` and `romanize(line: str) -> str`. Wrap an existing library or v1 module rather than writing a new algorithm.
2. Register it in `romanizers/__init__.py`.
3. Add its script/profile mapping to the table in `detect.py`.
4. Add the Whisper language code and any new setting (also to `.env.example`).
5. Add tests, a README row and a Credits entry.

## Tests
`python -m pytest` from `v2/` (with the venv active). Whisper and Genius are mocked; tests that need real audio use `@pytest.mark.audio` and are skipped by default. Fixtures are short inline UTF-8 samples plus `v1/lang_detection/*TestFile.txt` read in place. The Genius-format fixtures are hand-written; replace with a real dump when one exists.

## Known pitfalls
- **Python:** 3.14 breaks Whisper's dependencies. Use 3.12.
- **Encoding:** see conventions. Also `PYTHONUTF8=1` helps with subprocess output.
- **Alignment:** character count misaligns CJK (double width). Use `wcwidth.wcswidth`. Arabic is right-to-left: text passes through unchanged for now (known limitation, no bidi handling yet).
- **Whisper:** `result["text"]` has no line breaks; use `segments`. Music causes repeated or invented text and missed lines (use `condition_on_previous_text=False`, filter on `no_speech_prob`/`compression_ratio`, prefer `medium`). Vocal separation is on the roadmap, not built. Don't force a language for mixed-language songs.
- **Detection:** `langdetect` is nondeterministic (set `DetectorFactory.seed = 0`), unreliable on short lines, and has **no `sr` profile**. All mapping lives in one table in `detect.py`:

  | Input | Result |
  |---|---|
  | Hiragana/Katakana | ja |
  | Hangul | ko |
  | Arabic script | ar |
  | Cyrillic | sr (only Cyrillic language supported) |
  | Latin, langdetect `hr` / `sl` / `bs` | sr |
  | Latin, anything else (e.g. `en`) | und |
  | Han-only line | inherits the file-level result |
  | Whisper auto-detect `hr` / `bs` | sr |
- **Genius output:** contains other tags, a title line, `N Contributors`, and an `Embed` suffix on the last line. Don't match a fixed list of tags.
- **ffmpeg:** Whisper calls `ffmpeg` from `PATH`; `FFMPEG_PATH` is prepended to `PATH` at startup.
- **v1 oddities (report, don't fix):** `lang_detection/sample.py` points at missing `spanish.txt` and `arabic_portugueseTestFile.txt`; `arabicTestFile.txt` is prose, not lyrics; `korean_/arabic_romanize.py` need `input/` and `output/` folders that aren't in git.
