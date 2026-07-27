"""
tool_check.py
-------------
Detects whether yt-dlp (Python package) and ffmpeg (executable) are
available, so the app can show a clear message if something is missing.
"""

import shutil


def check_ytdlp() -> bool:
    try:
        import yt_dlp  # noqa: F401
        return True
    except ImportError:
        return False


def check_ffmpeg() -> bool:
    return shutil.which("ffmpeg") is not None


def missing_tools_message() -> str | None:
    missing = []
    if not check_ytdlp():
        missing.append(
            "yt-dlp (Python package) was not found.\n"
            "Install it with:  pip install yt-dlp"
        )
    if not check_ffmpeg():
        missing.append(
            "FFmpeg was not found. Please install FFmpeg or add it to your "
            "system PATH.\nDownload it from: https://ffmpeg.org/download.html\n"
            "(FFmpeg is only needed to merge separate video+audio streams for "
            "some sites/qualities - many downloads will work without it.)"
        )
    if not missing:
        return None
    return "\n\n".join(missing)
