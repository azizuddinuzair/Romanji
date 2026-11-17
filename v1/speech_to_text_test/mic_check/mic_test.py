"""
Microphone test. Run:  python test_mic.py
Optionally pass a device number:  python test_mic.py 2
Records 3 seconds and reports how loud the signal was.
"""

import sys

import numpy as np
import sounddevice as sd

SAMPLE_RATE = 16000

try:
    print("Available audio devices (input devices have 'in' > 0):\n")
    print(sd.query_devices())

    device = int(sys.argv[1]) if len(sys.argv) > 1 else None
    chosen = device if device is not None else sd.default.device[0]
    print(f"\nUsing input device: {chosen} -> {sd.query_devices(chosen)['name']}")

    print("\nRecording for 3 seconds... speak now!")
    audio = sd.rec(
        int(3 * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
        device=device,
    )
    sd.wait()

    peak = float(np.abs(audio).max())
    print(f"Peak level: {peak:.4f}  (0 = silence, 1 = maximum)")
    if peak < 0.005:
        print("RESULT: Essentially silent. Wrong device selected, mic muted, or "
              "microphone access is blocked in Windows privacy settings.")
    elif peak < 0.05:
        print("RESULT: Very quiet. Speak closer or raise the mic volume.")
    else:
        print("RESULT: Microphone works.")
except Exception as exc:
    print(f"\nERROR: {exc}")
    print("Check microphone permissions and that an input device is connected.")