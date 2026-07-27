# Video Downloader

A simple app that downloads full videos from YouTube, Vimeo, TikTok,
Twitter/X, Reddit, Facebook, and 1000+ other sites supported by yt-dlp.
No trimming - saves the complete video (or audio-only MP3) as-is.

## What's implemented

- Paste-a-URL, click-Download workflow with clipboard auto-detect
- Works with any site yt-dlp supports, not just YouTube
- Quality modes: Best Available / 1080p Compatibility / Audio Only (MP3)
- Settings remembered between runs (folder, quality, checkbox)
- Progress bar with percent / speed / ETA
- Friendly error messages for missing tools, bad URLs, unsupported
  links, and low disk space
- Dark, Windows-11-style UI (CustomTkinter) - same look as Aquarium Downloader

## Requirements

- Windows 11
- Python 3.10+
- **FFmpeg** on your system PATH - needed to merge separate video/audio
  streams and for MP3 extraction. Download from
  https://ffmpeg.org/download.html

## Setup (development / running from source)

```powershell
cd VideoDownloader
pip install -r requirements.txt
python main.py
```
(If `python` redirects to the Microsoft Store, use `py main.py` instead.)

## Building a standalone VideoDownloader.exe

```powershell
pyinstaller --noconfirm --onefile --windowed --name VideoDownloader main.py
```

The finished executable will be in `dist\VideoDownloader.exe`.

## Project structure

```
VideoDownloader/
├── main.py            # GUI + orchestration (CustomTkinter)
├── downloader.py       # yt-dlp wrapper: URL validation, format selection, progress
├── settings.py         # Persisted settings (JSON in %APPDATA%)
├── tool_check.py        # Detects yt-dlp / FFmpeg availability
└── requirements.txt
```
