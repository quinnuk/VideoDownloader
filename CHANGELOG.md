# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.3.0] - 2026-08-14

### Added
- Multiple simultaneous downloads (1–4), each with independent pause/resume/cancel
- Proper pause & resume that continues from where it left off instead of restarting
- Automatic retry for failed downloads, plus one-click "Retry All Failed"
- Playlist support with **Add All**, **Select Videos**, or a range (e.g. `1,3,7,10-15`)
- Optional browser cookies (Chrome/Edge/Firefox/Brave) for sites that require sign-in
- Persistent download history, separate from the live queue, with redownload/copy-link/open-folder actions
- Queue now persists between sessions with a resume prompt on next launch
- Drag & drop links onto the window
- Keyboard shortcuts (Ctrl+Enter to queue, Space to pause/resume, Delete to remove, see Help menu)
- Optional desktop notifications and a completion sound
- Format container choice (Best Available / MP4 / MKV / WEBM), remuxing instead of re-encoding where possible
- Selectable MP3 bitrate (128 / 192 / 256 / 320 kbps)
- Optional subtitles (None / English / All Available), embedded or as a separate file
- Optional download speed limit
- Settings export/import/reset from the Settings menu
- One-click yt-dlp update check from the Help menu
- Robust FFmpeg detection (bundled copy, app folder, or system PATH)
- Reliable duplicate detection that ignores tracking-parameter differences between links

### Changed
- Download quality options now range from Best Available down to 360p

## [1.0.0] - Initial release

### Added
- Core video/audio downloading via yt-dlp
- Video preview (title, uploader, duration, thumbnail) before downloading
- Sequential download queue with live progress, speed, and ETA
- MP3 audio extraction
- Clipboard URL detection
- Duplicate-file handling
- Persistent app settings

[Unreleased]: https://github.com/quinnuk/VideoDownloader/compare/v1.3.0...HEAD
[1.3.0]: https://github.com/quinnuk/VideoDownloader/releases/tag/v1.3.0
[1.0.0]: https://github.com/quinnuk/VideoDownloader/releases/tag/v1.0.0
