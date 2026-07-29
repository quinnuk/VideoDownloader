"""Small yt-dlp wrapper used by the desktop application."""

import re
import threading
from pathlib import Path
from typing import Callable, Optional

import yt_dlp

URL_RE = re.compile(r"^https?://", re.IGNORECASE)

FORMAT_SELECTORS = {
    "best": "bestvideo+bestaudio/best",
    "1080p": (
        "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/"
        "bestvideo[height<=1080]+bestaudio/best[height<=1080]"
    ),
    "audio_only": "bestaudio/best",
}


class DownloadCancelled(Exception):
    """Raised by the progress hook when the user cancels a queued download."""


class DownloadResult:
    def __init__(self, filepath: str, title: str):
        self.filepath = filepath
        self.title = title


def is_valid_url(url: str) -> bool:
    return bool(url) and bool(URL_RE.match(url.strip()))


def get_video_info(url: str) -> dict:
    """Return lightweight information for the preview panel without downloading.

    If the URL points at a playlist, returns {"is_playlist": True, "playlist_title": ...,
    "entries": [{"url": ..., "title": ...}, ...]} using yt-dlp's flat extraction, which is
    fast even for large playlists since it doesn't fetch full metadata per video.
    Otherwise returns the usual single-video info shape with "is_playlist": False.
    """
    probe_options = {
        "noplaylist": False,
        "quiet": True,
        "no_warnings": True,
        "extract_flat": "in_playlist",
    }
    with yt_dlp.YoutubeDL(probe_options) as ydl:
        info = ydl.extract_info(url, download=False)

    if info.get("_type") == "playlist" or "entries" in info:
        entries = []
        for entry in info.get("entries") or []:
            if not entry:
                continue
            entry_url = entry.get("url") or entry.get("webpage_url")
            if not entry_url:
                continue
            if not is_valid_url(entry_url):
                # Flat extraction sometimes returns a bare video ID rather than a full
                # URL for some sites; skip anything we can't turn into a real link.
                continue
            entries.append({
                "url": entry_url,
                "title": entry.get("title") or entry.get("id") or "Video",
            })
        return {
            "is_playlist": True,
            "playlist_title": info.get("title") or "Playlist",
            "entries": entries,
        }

    return {
        "is_playlist": False,
        "title": info.get("title", "Video"),
        "uploader": info.get("uploader") or info.get("channel"),
        "duration": info.get("duration"),
        "thumbnail": info.get("thumbnail"),
    }


def download_video(
    url: str,
    output_dir: str,
    quality: str,
    progress_callback: Optional[Callable[[dict], None]] = None,
    include_audio: bool = True,
    keep_original: bool = False,
    duplicate_mode: str = "Rename automatically",
    cancel_event: threading.Event | None = None,
    duplicate_callback: Optional[Callable[[str], str]] = None,
) -> DownloadResult:
    """Download one item, optionally without sound, and report its progress."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    is_audio = quality == "audio_only"
    video_only = not is_audio and not include_audio
    format_selector = (
        "bestvideo[ext=mp4]/bestvideo" if video_only
        else FORMAT_SELECTORS.get(quality, FORMAT_SELECTORS["best"])
    )

    def hook(data):
        if cancel_event is not None and cancel_event.is_set():
            raise DownloadCancelled()
        if progress_callback is None:
            return
        if data["status"] == "downloading":
            total = data.get("total_bytes") or data.get("total_bytes_estimate")
            downloaded = data.get("downloaded_bytes", 0)
            percent = (downloaded / total * 100) if total else None
            speed = data.get("speed")
            eta = data.get("eta")
            progress_callback({
                "status": "downloading", "percent": percent,
                "speed": f"{speed / 1024 / 1024:.1f} MB/s" if speed else "-",
                "eta": f"{eta // 60:02d}:{eta % 60:02d}" if eta else "-",
            })
        elif data["status"] == "finished":
            progress_callback({"status": "finished", "percent": 100.0})

    output_template = str(Path(output_dir) / "%(title)s.%(ext)s")
    if duplicate_mode == "Ask me":
        probe_options = {"outtmpl": output_template, "noplaylist": True, "quiet": True, "no_warnings": True}
        with yt_dlp.YoutubeDL(probe_options) as probe:
            probe_info = probe.extract_info(url, download=False)
            existing_path = Path(probe.prepare_filename(probe_info))
        if is_audio:
            existing_path = existing_path.with_suffix(".mp3")
        if existing_path.exists():
            action = duplicate_callback(str(existing_path)) if duplicate_callback else "skip"
            if action == "skip":
                raise FileExistsError(f"Skipped because this file already exists: {existing_path.name}")
            duplicate_mode = "Overwrite" if action == "overwrite" else "Rename automatically"

    ydl_opts = {
        "format": format_selector,
        "outtmpl": output_template,
        "progress_hooks": [hook],
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }
    if duplicate_mode == "Rename automatically":
        ydl_opts["outtmpl"] = str(Path(output_dir) / "%(title)s [%(id)s].%(ext)s")
    elif duplicate_mode == "Overwrite":
        ydl_opts["overwrites"] = True
    else:
        ydl_opts["nooverwrites"] = True

    if is_audio:
        ydl_opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192",
        }]
        ydl_opts["keepvideo"] = keep_original
    elif not video_only:
        ydl_opts["merge_output_format"] = "mp4"

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filepath = ydl.prepare_filename(info)

    if is_audio:
        final_path = str(Path(filepath).with_suffix(".mp3"))
    else:
        mp4_path = str(Path(filepath).with_suffix(".mp4"))
        final_path = mp4_path if Path(mp4_path).exists() else filepath
    if not Path(final_path).exists():
        final_path = filepath
    return DownloadResult(filepath=final_path, title=info.get("title", "video"))