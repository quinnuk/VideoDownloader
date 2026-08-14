"""
main.py
-------
Application entry point. Everything else lives in dedicated modules:

    ui.py               - the window and all user-facing widgets/dialogs
    queue_manager.py     - the live download queue (list ops, persistence)
    download_manager.py  - runs downloads concurrently against the queue
    downloader.py        - the yt-dlp wrapper itself
    models.py             - the DownloadItem/Status data model
    settings.py, history.py, queue_store.py, logging_setup.py, notifications.py,
    clipboard.py, thumbnail.py, tool_check.py, utils.py, version.py,
    ytdlp_updater.py     - supporting, single-purpose modules

Architecture: UI -> Queue Manager -> Download Manager -> Downloader -> yt-dlp.
"""

import os
import sys
from pathlib import Path

# When packaged as an .exe, make bundled tools such as FFmpeg discoverable.
if getattr(sys, "frozen", False):
    os.environ["PATH"] = str(Path(sys._MEIPASS)) + os.pathsep + os.environ.get("PATH", "")

# If a newer yt-dlp has been downloaded via Help > Check for yt-dlp Updates
# (see ytdlp_updater.py), put it at the front of sys.path so it shadows the
# version bundled inside this .exe. This MUST happen before anything else
# imports yt_dlp - ui.py and downloader.py both do, so this has to run
# before the `from ui import VideoDownloaderApp` line below.
from ytdlp_updater import override_dir  # noqa: E402

_ytdlp_override = override_dir() / "yt_dlp"
if _ytdlp_override.is_dir():
    sys.path.insert(0, str(_ytdlp_override.parent))

from ui import VideoDownloaderApp  # noqa: E402

if __name__ == "__main__":
    app = VideoDownloaderApp()
    app.mainloop()
