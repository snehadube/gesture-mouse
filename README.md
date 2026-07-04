# Gesture Mouse 🖐️🖱️

Control your mouse using hand gestures (via webcam + MediaPipe) and voice commands
(via speech recognition), built with Python.

## Features

- **Cursor movement** — move your index finger, cursor follows on screen.
- **Left click** — pinch index finger + thumb.
- **Right click** — pinch middle finger + thumb.
- **Scroll down** — pinch ring finger + thumb.
- **Voice commands** — say "chrome", "notepad", "music", or "close".
- Every action is logged with a timestamp to `log.txt`.

## Requirements

- Python 3.9 – 3.11 (MediaPipe does not yet support the newest Python versions)
- A working webcam
- Windows (uses `win+r` / notepad / wmplayer — voice commands are Windows-specific;
  gesture control itself is cross-platform)

## Setup

\`\`\`bash
git clone https://github.com/<your-username>/gesture-mouse.git
cd gesture-mouse

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
\`\`\`

> **Note (Windows):** `PyAudio` sometimes fails to install via pip. If it does, download
> the matching wheel from https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio and install
> with `pip install <downloaded_file>.whl`.

## Run

\`\`\`bash
python gesture_mouse.py
\`\`\`

Press **ESC** with the webcam window focused to quit.

## Known limitations

- Voice commands (`win+r`, `notepad.exe`, `wmplayer`) only make sense on Windows.
- Runs one hand at a time (`max_num_hands=1`) for stability; can be increased in code.
- Lighting and camera quality affect hand-tracking accuracy.

## License

MIT