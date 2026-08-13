# Changelog

All notable changes to Video Downloader Pro are documented here.

> **Note on version numbers below 1.3.0:** `version.py` (the single source of
> truth for the app's version) wasn't introduced until partway through this
> round of work. The 1.1.0 and 1.2.0 entries below are assigned retroactively
> to the commits/state that existed at each point, grouped by the roadmap
> phases they correspond to.

## [1.3.0] - Phase 5: Advanced Features

### Added
- Browser cookie support (Chrome/Edge/Firefox/Brave) for sites that require sign-in. Cookie data is read directly by yt-dlp from the browser's local profile - never displayed, logged, or transmitted by this app; only the browser name is ever stored in settings.
- A "Retry with Browser Cookies" quick action on failed downloads whose error indicates a login/sign-in requirement.
- Playlist handling now offers a real three-way choice - **Add All**, **Select Videos**, or **Cancel** - matching the original spec exactly.
- A video-selection window for playlists: multi-select list, Select All/Select None, and a range field (e.g. `1,3,7,10-15`).
- "Check for yt-dlp Updates" in the Help menu, checking the installed version against PyPI's latest (only on request, never automatically).
- Installed yt-dlp version shown in the About window.
- Settings menu: **Export Settings**, **Import Settings**, and **Reset Settings**.

### Changed
- The old binary "add all vs. just this link" playlist prompt was replaced by the three-way choice above; the implicit "just add the single link" fallback no longer exists (use Select Videos to pick one specific video instead).

## [1.2.0] - Phase 4 (User Experience) + architecture split

### Added
- Optional desktop notifications (download complete / failed / queue complete) and an optional sound on queue completion, via a dependency-free PowerShell toast helper.
- Drag-and-drop: dropping a link onto the window fills the URL box (optional dependency, `tkinterdnd2`; the app runs unaffected if it isn't installed).
- Keyboard shortcuts: Ctrl+V (paste), Enter (preview), Ctrl+Enter (add to queue), Space (pause/resume selected), Delete (remove selected), Ctrl+A (select all in the focused field), Ctrl+R (retry all failed).
- Richer failure dialog: reason-specific "Possible solutions" list, with full technical detail behind a "Show Technical Details" toggle instead of always visible.
- Live progress shown in the window title bar (e.g. "3/12 done, 2 downloading").
- Help menu with an About window (version, yt-dlp/FFmpeg credits, GitHub link) and a Troubleshooting & Shortcuts window.

### Changed
- **Major internal refactor:** `main.py` was split into focused modules matching the intended architecture (UI -> Queue Manager -> Download Manager -> Downloader -> yt-dlp):
  - `ui.py` - window, widgets, and dialogs only
  - `queue_manager.py` - the live download queue (add/remove/reorder/retry/persist), no UI dependency
  - `download_manager.py` - runs downloads concurrently, one `DownloadControl` per active item
  - `clipboard.py` / `thumbnail.py` - clipboard polling and preview/thumbnail loading, extracted from the UI
  - `main.py` reduced to a ~20-line entry point
- Verified with a full import pass (stubbed dependencies) and a custom undefined-name sweep across every function in every module; no circular imports.

## [1.1.0] - Phases 1-3: Reliability, Queue Improvements, Download Features

### Added
- **Reliability (Phase 1):**
  - Proper pause/resume: pausing keeps the partial file and resumes from where it left off; cancelling abandons the download and removes the partial file. States are now `Queued / Downloading / Paused / Completed / Failed / Cancelled`.
  - Retry Failed and Retry All Failed.
  - Failure dialog showing the specific reason, with Retry and Copy Error actions.
  - Thumbnail race-condition fix: every preview request is tagged, so a slow response for an earlier link can never land on a newer preview.
  - "Open folder when queue finishes" now opens the folder of the last *successful* download, never the last queue item regardless of whether it failed.
  - Clean shutdown: clipboard polling and any in-flight download are stopped when the window closes.
  - Robust FFmpeg detection: bundled directory -> app folder -> system PATH, in that order.
  - Windows-safe filenames (illegal characters, reserved names, length limits) and a clear error instead of a crash on overly long paths.
  - Duplicate detection that ignores tracking query parameters (`?utm_source=...` etc.).
  - Basic application logging (startup/shutdown, download start/finish/failure, kept free of cookies/passwords/tokens).
- **Queue improvements (Phase 2):**
  - Move Up/Move Down, queue statistics (completed/downloading/queued/failed counts, overall %), queue persistence across restarts (with a "Resume queue?" prompt, never auto-restarting), and a persistent download history separate from the live queue.
- **Download features (Phase 3):**
  - Expanded quality options (Best Available down to 360p, or Audio Only) with graceful fallback to the closest available resolution.
  - Format/container selection (Best Available / MP4 / MKV / WEBM), remuxing instead of forcing a re-encode.
  - Subtitle support (None / English / All Available), embedded or as a separate file.
  - Download speed limiting and 1-4 simultaneous downloads, each with its own independent pause/cancel control.
  - Automatic network retry (3 attempts, 5-second delay) for transient errors; permanent errors are not retried.

## [1.0.0] - Baseline

The original project prior to this round of work: video/MP3 downloads via yt-dlp, multiple download queue, video preview, playlist link handling, clipboard URL detection, progress/speed/ETA display, duplicate handling, persistent settings, Windows installer, bundled FFmpeg, PyInstaller packaging.
