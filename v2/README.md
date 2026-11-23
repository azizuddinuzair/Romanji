# Romanji v2

Romanji takes a song, gets its lyrics, romanizes them, and shows the original and the romanized text side by side.

**Status:** v2 is in the design stage. This README describes the intended behavior; the commands below work once the code lands (see Roadmap).

## Supported languages
| Language | Code | Library (from v1) |
|---|---|---|
| Japanese | `ja` | pykakasi |
| Korean | `ko` | korean_romanizer |
| Arabic | `ar` | arabic2latin |
| Serbian (Cyrillic or Latin) | `sr` | built-in table |

Detection works per line, so a Japanese song with English lines is fine: Latin-script lines stay as they are.

## Prerequisites
- Windows with PowerShell. Python **3.12** (Whisper's dependencies don't support 3.14 yet; the repo-root `.python-version` says 3.14, v2 uses its own).
- **ffmpeg** on `PATH` (or `FFMPEG_PATH` in `.env`), for audio mode only.
- A **Genius API token** (https://genius.com/api-clients), for title/artist lookup only.

## Install
```powershell
cd v2
winget install Python.Python.3.12       # if `py -3.12 --version` fails
winget install Gyan.FFmpeg              # audio mode only
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1            # if blocked: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
pip install -r requirements.txt
pip install -r requirements-audio.txt   # audio mode only (downloads torch, large)
Copy-Item .env.example .env
```
Then open `.env` and paste your token after `GENIUS_ACCESS_TOKEN=`. `.env` is gitignored; never commit it.

### Settings (`.env`)
`GENIUS_ACCESS_TOKEN`, `WHISPER_MODEL` (tiny…large, default small), `WHISPER_DEVICE` (auto/cpu/cuda), `DEFAULT_LANGUAGE` (blank = auto), `JAPANESE_ROMANIZATION` (hepburn/kunrei/passport), `OUTPUT_DIR`, `FFMPEG_PATH`, `ALIGN_WIDTH`, `LANG_CONFIDENCE`. Each is documented in `.env.example`.

## Usage
```powershell
python -m romanji text lyrics.txt                      # a lyrics file
python -m romanji genius "Yoru ni Kakeru" "YOASOBI"    # lookup on Genius (needs token)
python -m romanji audio song.mp3                       # transcribe with Whisper
python -m romanji audio song.mp3 --lrc --save          # also write .lrc + .txt to OUTPUT_DIR
```
Audio mode keeps Whisper's timestamps; `--lrc` writes `<name>.lrc` (original) and `<name>.romanized.lrc`.

## Sample output (illustrative, `ALIGN_WIDTH=30`)
```
沈むように溶けてゆくように     | shizumu you ni tokete yuku you ni
Baby, I'm falling              | Baby, I'm falling
사랑해 너를                    | saranghae neoreul
Ја волим тебе                  | Ja volim tebe
```
Widths are measured in display columns, so double-width CJK lines line up. Arabic is right-to-left and is shown unchanged; terminals vary in how they draw it. (An Arabic example will be added once the romanizer runs.)

## Notes for Windows
- Use Windows Terminal for CJK/Arabic display. Output is always UTF-8.
- Songs are harder than speech: background music can make Whisper skip or invent lines. Use `WHISPER_MODEL=medium` for better results.

## Roadmap
- [ ] Text, Genius and audio pipeline; CLI; `.txt` and `.lrc` output
- [ ] Optional vocal separation (e.g. Demucs) before Whisper
- [ ] Right-to-left (bidi) handling for Arabic
- [ ] `.html` / `.json` output
- Mic recording and the Tkinter GUI live in `v1/speech_to_text_test` for now (credit: ComicShadow); they are planned for a later v2 GUI.

## Differences from v1
- v1 is separate prototypes; v2 is one pipeline with one CLI.
- Both text and audio input; Whisper segments restore line structure, language is picked per line (not by hand, not per file).
- All file I/O is UTF-8; no hardcoded folders or `input()` in library code.
- Alignment uses display width instead of character count.
- Cleaning handles any bracketed section tag plus Genius header/footer junk, not just three prefixes.
- One romanizer interface (`romanize(line, lang)`). v2 reuses v1's code; v1 is left unchanged.

## Credits
v2 builds on the v1 modules written by the team (names as in git history; some are GitHub handles).

| Contributor | Module |
|---|---|
| JasmithaK (handle) | Language detection |
| Vincent Mei | Line matching |
| Abhi Seela | Lyric cleaner (Genius) |
| Pprajapati7964 (handle) | Japanese romanization |
| Diego | Serbian romanization |
| Quang Duc Lam Nguyen | Korean and Arabic romanization |
| ComicShadow (handle) | Whisper speech-to-text app, mic test |
| Uzair Azizuddin | Project setup |
