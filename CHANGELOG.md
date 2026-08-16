# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.3.1] - 2026-08-16

### Fixed
- `version.APP_VERSION` was still `1.2.0` while the README, installer, and this changelog had all moved to `1.3.0`; the About dialog now reports the correct version
- Main window subtitle still said downloads happen "one at a time", left over from before 1.3.0 added simultaneous downloads

### Changed
- Removed unused `downloader.is_valid_youtube_url()` and consolidated the two separate yt-dlp-version lookups (`downloader.get_installed_version()` and an inline duplicate in the update checker) into one
- Removed an unused `urllib.request` import and two redundant local `json` imports in `ui.py`
- The "already in queue" confirmation dialog was duplicated in two places in `ui.py`; extracted into one shared helper
- `build_installer.bat` now builds from `Video_Downloader.spec` (same as `build_exe.bat`) instead of a separate, hand-rolled PyInstaller command that could silently drift out of sync with it
- `Video_Downloader.spec`'s FFmpeg path no longer falls back to a hardcoded path from one developer's machine; it now auto-detects `ffmpeg` on `PATH` (or `FFMPEG_PATH` if set) and fails with a clear error if neither is found
- Split `pyinstaller` out of `requirements.txt` into a new `requirements-build.txt`, since it's only needed to package the app, not to run it from source

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

[Unreleased]: https://github.com/quinnuk/VideoDownloader/compare/v1.3.1...HEAD
[1.3.1]: https://github.com/quinnuk/VideoDownloader/compare/v1.3.0...v1.3.1
[1.3.0]: https://github.com/quinnuk/VideoDownloader/compare/v1.0.0...v1.3.0
[1.0.0]: https://github.com/quinnuk/VideoDownloader/releases/tag/v1.0.0