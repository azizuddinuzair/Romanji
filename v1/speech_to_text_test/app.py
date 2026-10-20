
# Voice-to-Text with OpenAI Whisper
# ---------------------------------
# Record your voice from the microphone (or load an audio file) and get a
# transcript written in the language you chose: Arabic, Korean, or Japanese.

# Whisper's task="transcribe" keeps the output in the original language
# (it does NOT translate to English). The chosen language is passed to
# Whisper explicitly, so it never guesses a different one.

# dependencies
# ffmpeg

#Test version 1

import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import numpy as np
import sounddevice as sd

SAMPLE_RATE = 16000  # Whisper expects 16 kHz mono audio
MODEL_CHOICES = ["tiny", "base", "small", "medium", "large"]

# Display name to Whisper language code
SUPPORTED_LANGUAGES = {
    "Arabic (العربية)": "ar",
    "Korean (한국어)": "ko",
    "Japanese (日本語)": "ja",
}

#Deadass don't ask me abt this class

#Initially plan was to use a siple TK inter GUI, add mp3 files to project folder
#and use that to test whisper functionality

#Upgraded program with AI assistance to enable adding mp3 files from user directory
#and also recording

#Referred to this repo for documentation: https://github.com/openai/whisper

class VoiceToTextApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Whisper Voice-to-Text")
        self.geometry("720x560")
        self.minsize(560, 440)

        # State
        self._models = {}  # cache: model name -> loaded model
        self._frames = []  # recorded audio chunks
        self._stream = None
        self._record_start = 0.0
        self._recording = False
        self._busy = False

        self._whisper = None  # set once the libraries finish loading
        self._torch = None

        self._build_ui()

        # Make sure the window isn't hidden behind VS Code
        self.lift()
        self.attributes("-topmost", True)
        self.after(500, lambda: self.attributes("-topmost", False))

        # Load the heavy libraries without freezing the window
        self._set_busy(True, "Loading Whisper libraries (first launch can take a minute)…")
        threading.Thread(target=self._load_libraries, daemon=True).start()

    def _load_libraries(self):
        try:
            import torch
            import whisper

            self._torch = torch
            self._whisper = whisper
            self.after(0, lambda: self._set_busy(False, "Ready."))
        except Exception as exc:
            self.after(
                0,
                lambda: (
                    self._set_busy(True, "Failed to load Whisper."),
                    messagebox.showerror(
                        "Import error",
                        "Could not load torch/whisper:\n"
                        f"{exc}\n\nRun: pip install -r requirements.txt",
                    ),
                ),
            )

    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        pad = {"padx": 10, "pady": 6}

        # Settings row
        settings = ttk.Frame(self)
        settings.pack(fill="x", **pad)

        ttk.Label(settings, text="Model:").pack(side="left")
        self.model_var = tk.StringVar(value="small")
        ttk.Combobox(
            settings,
            textvariable=self.model_var,
            values=MODEL_CHOICES,
            state="readonly",
            width=8,
        ).pack(side="left", padx=(4, 16))

        ttk.Label(settings, text="Language:").pack(side="left")
        self.lang_var = tk.StringVar(value=list(SUPPORTED_LANGUAGES)[0])
        ttk.Combobox(
            settings,
            textvariable=self.lang_var,
            values=list(SUPPORTED_LANGUAGES),
            state="readonly",
            width=20,
        ).pack(side="left", padx=4)

        # Buttons row
        buttons = ttk.Frame(self)
        buttons.pack(fill="x", **pad)

        self.record_btn = ttk.Button(
            buttons, text="● Start Recording", command=self.toggle_recording
        )
        self.record_btn.pack(side="left")

        self.file_btn = ttk.Button(
            buttons, text="Open Audio File…", command=self.transcribe_file
        )
        self.file_btn.pack(side="left", padx=8)

        self.timer_var = tk.StringVar(value="")
        ttk.Label(buttons, textvariable=self.timer_var).pack(side="left", padx=8)

        # Transcript box
        frame = ttk.Frame(self)
        frame.pack(fill="both", expand=True, **pad)
        self.text = tk.Text(frame, wrap="word", font=("TkDefaultFont", 13))
        scroll = ttk.Scrollbar(frame, command=self.text.yview)
        self.text.configure(yscrollcommand=scroll.set)
        self.text.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        # Bottom row
        bottom = ttk.Frame(self)
        bottom.pack(fill="x", **pad)
        ttk.Button(bottom, text="Copy", command=self.copy_text).pack(side="left")
        ttk.Button(bottom, text="Save…", command=self.save_text).pack(side="left", padx=8)
        ttk.Button(bottom, text="Clear", command=self.clear_text).pack(side="left")

        # Status bar
        self.status_var = tk.StringVar(value="Ready.")
        ttk.Label(self, textvariable=self.status_var, relief="sunken", anchor="w").pack(
            fill="x", side="bottom"
        )

    # ------------------------------------------------------------ Recording
    def toggle_recording(self):
        if self._busy:
            return
        if self._recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        self._frames = []
        try:
            self._stream = sd.InputStream(
                samplerate=SAMPLE_RATE,
                channels=1,
                dtype="float32",
                callback=self._on_audio,
            )
            self._stream.start()
        except Exception as exc:  # no mic, permission denied, etc.
            messagebox.showerror("Microphone error", f"Could not open microphone:\n{exc}")
            return

        self._recording = True
        self._record_start = time.time()
        self.record_btn.config(text="■ Stop & Transcribe")
        self.file_btn.config(state="disabled")
        self.status_var.set("Recording… speak now.")
        self._tick_timer()

    def _on_audio(self, indata, frames, time_info, status):
        self._frames.append(indata.copy())

    def _tick_timer(self):
        if self._recording:
            elapsed = int(time.time() - self._record_start)
            self.timer_var.set(f"{elapsed // 60:02d}:{elapsed % 60:02d}")
            self.after(250, self._tick_timer)

    def stop_recording(self):
        self._recording = False
        self._stream.stop()
        self._stream.close()
        self._stream = None
        self.timer_var.set("")
        self.record_btn.config(text="● Start Recording")

        if not self._frames:
            self.status_var.set("No audio captured.")
            self.file_btn.config(state="normal")
            return

        audio = np.concatenate(self._frames, axis=0).flatten().astype(np.float32)
        if len(audio) < SAMPLE_RATE * 0.5:
            self.status_var.set("Recording too short — try again.")
            self.file_btn.config(state="normal")
            return

        self._start_transcription(audio)

    # ------------------------------------------------------------ File input
    def transcribe_file(self):
        if self._busy or self._recording:
            return
        path = filedialog.askopenfilename(
            title="Choose an audio file",
            filetypes=[
                ("Audio files", "*.wav *.mp3 *.m4a *.flac *.ogg *.webm *.mp4"),
                ("All files", "*.*"),
            ],
        )
        if not path:
            return

        model_name, lang_code = self._settings()

        def load_and_run():
            try:
                audio = self._whisper.load_audio(path)  # requires ffmpeg
            except Exception as exc:
                self.after(
                    0,
                    lambda: self._finish_error(
                        f"Could not read file (is ffmpeg installed?):\n{exc}"
                    ),
                )
                return
            self._transcribe_worker(audio, model_name, lang_code)

        self._set_busy(True, "Loading audio file…")
        threading.Thread(target=load_and_run, daemon=True).start()

    # --------------------------------------------------------- Transcription
    def _settings(self):
        """Read GUI settings on the main thread (Tk is not thread-safe)."""
        return self.model_var.get(), SUPPORTED_LANGUAGES[self.lang_var.get()]

    def _start_transcription(self, audio):
        model_name, lang_code = self._settings()
        self._set_busy(True, "Transcribing…")
        threading.Thread(
            target=self._transcribe_worker,
            args=(audio, model_name, lang_code),
            daemon=True,
        ).start()

    def _get_model(self, name):
        if name not in self._models:
            self.after(
                0,
                lambda: self.status_var.set(
                    f"Loading '{name}' model (first run downloads it)…"
                ),
            )
            self._models[name] = self._whisper.load_model(name)
        return self._models[name]

    def _transcribe_worker(self, audio, model_name, lang_code):
        try:
            model = self._get_model(model_name)
            self.after(0, lambda: self.status_var.set("Transcribing…"))

            result = model.transcribe(
                audio,
                task="transcribe",  # keep the original language, no translation
                language=lang_code,  # ar / ko / ja, chosen by the user
                fp16=self._torch.cuda.is_available(),
            )
            text = result["text"].strip()
            self.after(0, lambda: self._finish_ok(text))
        except Exception as exc:
            self.after(0, lambda: self._finish_error(str(exc)))

    def _finish_ok(self, text):
        if text:
            if self.text.get("1.0", "end").strip():
                self.text.insert("end", "\n\n")
            self.text.insert("end", text)
            self.text.see("end")
        self._set_busy(False, "Done." if text else "No speech detected.")

    def _finish_error(self, message):
        self._set_busy(False, "Error.")
        messagebox.showerror("Transcription error", message)

    def _set_busy(self, busy, status):
        self._busy = busy
        state = "disabled" if busy else "normal"
        self.record_btn.config(state=state)
        self.file_btn.config(state=state)
        self.status_var.set(status)

    # ------------------------------------------------------- Text utilities
    def copy_text(self):
        content = self.text.get("1.0", "end").strip()
        if content:
            self.clipboard_clear()
            self.clipboard_append(content)
            self.status_var.set("Copied to clipboard.")

    def save_text(self):
        content = self.text.get("1.0", "end").strip()
        if not content:
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt", filetypes=[("Text file", "*.txt")]
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            self.status_var.set(f"Saved to {path}")

    def clear_text(self):
        self.text.delete("1.0", "end")


if __name__ == "__main__":
    VoiceToTextApp().mainloop()