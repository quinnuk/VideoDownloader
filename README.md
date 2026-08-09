# AudioCleaner

[![Windows](https://img.shields.io/badge/platform-Windows-blue)](https://img.shields.io/badge/platform-Windows-blue) [![Python](https://img.shields.io/badge/python-3.10+-yellow)](https://img.shields.io/badge/python-3.10+-yellow) [![License](https://img.shields.io/badge/license-BSD--2--Clause-green)](LICENSE)

A minimal, "set it and forget it" Windows app that scans a folder of MKV files (recursively) and keeps only the single best English audio track per file — Dolby Atmos always wins when present — while never touching video, subtitles, chapters, fonts, attachments, or metadata.

<p align="center">
  <a href="https://buymeacoffee.com/quinnuk" target="_blank">
    <img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="50" width="180">
  </a>
  <br>
  <sub>If AudioCleaner saves you disk space, a coffee is always appreciated ☕</sub>
</p>

---

## 🖥 Screenshot

![AudioCleaner main window](screenshot.jpg)

---

## Requirements

- **Python 3.10+**
- **[MKVToolNix](https://mkvtoolnix.download/)** — provides `mkvmerge`, used to inspect and remux files. Must be on your `PATH`, **or** its executable placed in the same folder as `AudioCleaner.exe`.
- **[MediaInfo](https://mediaarea.net/en/MediaInfo)** (CLI edition) — used alongside mkvmerge to reliably detect Atmos / DTS:X extensions. Must be on your `PATH`, **or** its executable placed in the same folder as `AudioCleaner.exe`.

If you're running the standalone `.exe`, keeping `MediaInfo.exe` (and its `Contrib`/`Plugin` folders if present) directly next to `AudioCleaner.exe` is the simplest option and avoids needing a system-wide install.

Check both are installed and on PATH:

```
mkvmerge --version
mediainfo --version
```

## Setup

```
pip install -r requirements.txt
python main.py
```

## How it works

1. **Add your folders** — click "Add Folder…" once per movie/TV library. They can be on completely different drives with no shared parent — each is tracked independently, with its own cache and log file living inside that folder.
2. **Scan** — recursively finds every `.mkv` file under the selected folder. Metadata is probed in parallel (mkvmerge + mediainfo) and cached in `.audiocleaner_cache.json` in the root folder, so re-runs on an unchanged library are near-instant.
3. **Select** — for each file, ranks all English audio tracks by codec quality (Atmos+TrueHD > DTS:X > TrueHD > DTS-HD MA > LPCM > FLAC > E-AC3 > DTS > AC3 > AAC > MP3) and picks the best.
4. **Process** — files with only one audio track (already English) are left alone. Everything else is remuxed to a temp file (`name.ac_tmp.mkv`) containing only the chosen audio track — video is never re-encoded, and subtitles/chapters/fonts/attachments/metadata are preserved by mkvmerge's default behavior.
5. **Verify & replace** — the temp file is probed to confirm it has exactly one audio track in the expected language. Only then does it atomically replace the original (`os.replace`). If verification fails, the temp file is discarded and the original is never touched.
6. **Log** — every decision is appended to `audiocleaner_log.txt` in the root folder, viewable via the "Open Log" button.

## Watch Mode, system tray & autostart

Beyond a one-off scan, AudioCleaner can run continuously in the background and clean new files as they arrive — useful if it's paired with something like Radarr/Sonarr dropping files into your library.

- **Start Watching All Folders** — instead of a single scan-and-stop pass, this keeps a lightweight watcher running per folder that detects new/changed `.mkv` files, waits for them to finish copying (the "Wait for new files to finish copying" setting — default 120s, matching typical Radarr/Sonarr move behaviour), then cleans them automatically using the same select → process → verify → replace pipeline as a manual run.
- **System tray** — closing the window (the X button) doesn't quit the app; it minimises to a tray icon instead, so watching continues in the background. Right-click the tray icon for Show Window, Start/Stop Watching, and Quit AudioCleaner. Quit is the only way to fully exit while watching.
- **Start with Windows** — tick the checkbox to have AudioCleaner launch automatically at login, minimised straight to the tray, and resume watching whatever folders you'd previously added. This adds a per-user entry to `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` (no admin rights required); unticking removes it. Your folder list and the "wait for new files" setting are remembered between sessions either way.

## Building a standalone .exe

If you'd rather double-click an app than run `python main.py`, you can bundle it into a single `AudioCleaner.exe` with PyInstaller. This has to be built **on Windows** (PyInstaller packages against the OS it runs on).

1. Make sure `pip install -r requirements.txt` has already been run.
2. Double-click **`build.bat`** in this folder (or run it from a Command Prompt).
3. It installs PyInstaller if needed, then builds. When it finishes, your exe is at `dist\AudioCleaner.exe` — copy that one file anywhere you like (e.g. Desktop, or next to your media library) and run it directly. No Python installation is needed on the machine you copy it to.

Notes:

- First launch of a `--onefile` build is a bit slower (a second or two) because it unpacks itself into a temp folder each run — that's normal.
- mkvmerge and mediainfo still need to be installed separately (on PATH, or placed next to the exe — see Requirements above); the exe still checks for them and shows the same download banner if they're missing.
- Rebuilding: just re-run `build.bat` any time you get updated source files — it overwrites the previous `dist\AudioCleaner.exe`.

## Codec detection caveat

Atmos and DTS:X are extensions layered on top of TrueHD/DTS, and are not always exposed cleanly by either tool alone. This app cross-references mkvmerge's codec string with mediainfo's commercial-name and additional-features fields. It's the standard practical approach, but on unusual/malformed files it's worth spot-checking the log the first time you run it against a new library.

## Project layout

```
audiocleaner/
  config.py      codec priority list & constants
  probe.py       mkvmerge/mediainfo wrappers + on-disk cache
  codec_rank.py  codec classification & best-track selection
  processor.py   safe remux -> verify -> atomic replace
  scanner.py     recursive file discovery + pipeline orchestration
  watcher.py     folder watching for continuous/background cleaning
  worker.py      QThread wrapper (keeps GUI responsive)
  gui.py         PySide6 single-page interface
  autostart.py   Windows "start with Windows" (HKCU Run key) support
main.py          entry point
```

## ☕ Support This Project

AudioCleaner is free and built in my spare time. If it's useful to you, consider buying me a coffee — it's a big help and genuinely appreciated.

<p align="center">
  <a href="https://buymeacoffee.com/quinnuk" target="_blank">
    <img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="50" width="180">
  </a>
</p>
