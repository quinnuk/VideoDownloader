# 🎬 Video Downloader Pro

A modern Windows video downloader with a simple, user-friendly interface powered by **yt-dlp**.

Download videos and audio from your favourite websites with support for thousands of online platforms.

[![Windows](https://img.shields.io/badge/platform-Windows-blue)](https://img.shields.io/badge/platform-Windows-blue) [![Python](https://img.shields.io/badge/python-3.x-yellow)](https://img.shields.io/badge/python-3.x-yellow) [![License](https://img.shields.io/badge/license-MIT-green)](LICENSE) [![Version](https://img.shields.io/badge/version-1.3.1-orange)](CHANGELOG.md)

<p align="center">
  <a href="https://buymeacoffee.com/quinnuk" target="_blank">
    <img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="60" width="217">
  </a>
  <br>
  <sub>If Video Downloader Pro saves you time, a coffee is always appreciated ☕</sub>
</p>

---

## ✨ Features

### 🎥 Video Downloads

- Download videos from YouTube, Vimeo, TikTok, Reddit, Facebook, X/Twitter and many more
- Powered by the reliable **yt-dlp** engine
- Supports thousands of websites
- Paste a playlist link and choose **Select All/None**, check individual videos, or type a **range** (e.g. `1,3,7,10-15`) — or just add the single pasted link instead
- Optional browser cookies (Chrome/Edge/Firefox/Brave), set once in **Settings > Preferences**, for sites that require sign-in — read directly by yt-dlp, never stored, displayed, or logged by this app

### 👀 Video Preview

Before downloading, preview:

- Video title
- Creator/uploader
- Duration
- Thumbnail

### 📥 Download Management

- Multiple downloads at once (1–4 simultaneous), each with independent pause/resume/cancel
- Proper pause & resume — a paused download picks up from where it left off, not from zero
- Automatic retry for failed downloads, plus a one-click **Retry All Failed**
- Failed downloads show the actual reason and suggested fixes, with full technical details on request
- Live per-item progress, overall queue progress bar, and queue statistics (completed/downloading/queued/failed counts)
- Queue is remembered between sessions — you'll be asked whether to resume it on next launch
- Persistent download history (separate from the live queue), with redownload/copy-link/open-folder actions
- Drag & drop a link onto the window, or use keyboard shortcuts (Ctrl+Enter to queue, Space to pause/resume, Delete to remove, and more — see the Help menu)
- Right-click any item in the queue for actions (retry, remove, open file/folder, move up/down, and more) instead of a wall of buttons
- Optional desktop notifications and a sound when the queue finishes
- Reliable duplicate detection, even when links differ only by tracking parameters

### 🎵 Audio & Format Options

- Extract audio as MP3, with your choice of bitrate (128 / 192 / 256 / 320 kbps)
- Quality options from Best Available down to 360p, or Audio Only
- Choose a container (Best Available / MP4 / MKV / WEBM) — remuxes instead of re-encoding wherever possible
- Optional subtitles (None / English / All Available), embedded or as a separate file
- Optional download speed limit (1/2/5/10 MB/s or a custom value)

### ⚙️ Smart Features

- Remembers your settings; export/import/reset them from **Settings > Preferences**
- Everyday, per-download choices (quality, format, subtitles, output folder) stay on the main screen; things you set once (speed limit, simultaneous downloads, notifications, duplicate handling, browser cookies) live in the Settings dialog to keep the window compact
- Clipboard URL detection
- Robust FFmpeg detection (bundled copy, app folder, or system PATH)
- One-click yt-dlp updates from the Help menu — checks your version against the latest release and installs it for you, whether you're running from source or the packaged .exe (takes effect on restart)
- Simple Windows desktop interface

---

## 🖥 Screenshots

![Main window](screenshots/main-window.png)

---

## 📦 Installation

### Option 1 — Installer (Recommended)

[![Download Latest Version](https://img.shields.io/badge/Download-Latest%20Version-blue?style=for-the-badge&logo=windows)](https://github.com/quinnuk/VideoDownloader/releases/latest/download/VideoDownloader-Setup.exe)

Run the installer and follow the instructions. FFmpeg is bundled, so there's nothing extra to install.

> **Note:** Since this app isn't code-signed, Windows SmartScreen may show a "Windows protected your PC" warning the first time you run the installer. This is normal for small independent apps — click **More info**, then **Run anyway** to continue.

### Option 2 — Run from Source

Requirements:

- Windows 10/11
- Python 3.x
- **[FFmpeg](https://ffmpeg.org/download.html)** — required for merging video/audio streams and MP3 extraction. Must be on your system `PATH`.

Install dependencies:

```
pip install -r requirements.txt
```

Then launch the app:

```
python main.py
```

Or on Windows, just double-click `run.bat`.

---

## ▶️ Usage

1. Paste a video link into the **Video URL** box (or copy one — it's detected automatically), or drag a link onto the window.
2. Click **Preview** to check the title, uploader, duration, and thumbnail before downloading. Pasting a playlist link opens a picker instead.
3. Choose your **Download Quality** (Best Available down to 360p, or Audio Only/MP3), **Format**, **Subtitles**, and output folder. If you pick Audio Only, you can also set the **MP3 Bitrate**.
4. Click **Add to Queue** — repeat for as many links as you like. Pasting a playlist link opens a picker where you can select all, check individual videos, or type a range.
5. Click **Start Queue** to begin downloading. Live progress, queue statistics, and overall progress are shown as it runs; use **Pause Selected** or **Stop Queue** at any time — both resume properly rather than restarting from zero.
6. Once finished, right-click a queue item (or use the **History** button) for open-file/open-folder/redownload actions.

Check the **Settings** menu for speed limiting, simultaneous downloads, notifications, browser cookies, and settings export/import/reset, and the **Help** menu for keyboard shortcuts, troubleshooting, and **Check for yt-dlp Updates** — if a newer version is available, click **Update Now** (or **Download & Install** on the packaged .exe) and restart the app to pick it up. This is the fastest fix if downloads suddenly start failing on a site that used to work, since sites change things yt-dlp needs updating for.

---

## ☕ Support This Project

Video Downloader Pro is free and built in my spare time. If it's useful to you, consider buying me a coffee — it's a big help and genuinely appreciated.

<p align="center">
  <a href="https://buymeacoffee.com/quinnuk" target="_blank">
    <img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="50" width="180">
  </a>
</p>
