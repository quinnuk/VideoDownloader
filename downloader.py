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

# Templates used to reconstruct a full URL when flat playlist extraction only
# gives us a bare video ID for a site we recognise. Extend as needed.
KNOWN_ENTRY_URL_TEMPLATES = {
    "Youtube": "https://www.youtube.com/watch?v={id}",
    "YoutubeTab": "https://www.youtube.com/watch?v={id}",
    "Vimeo": "https://vimeo.com/{id}",
}


class DownloadCancelled(Exception):
    """Raised when the user cancels a queued download."""


class DownloadSkipped(Exception):
    """Raised when the user chooses to skip a download because the file already exists.

    Kept separate from other failures so callers can show "Skipped" rather than
    "Failed" for a deliberate user choice.
    """


class DownloadResult:
    def __init__(self, filepath: str, title: str):
        self.filepath = filepath
        self.title = title


def is_valid_url(url: str) -> bool:
    return bool(url) and bool(URL_RE.match(url.strip()))


def _resolve_entry_url(entry: dict) -> Optional[str]:
    """Return a usable URL for a flat-extracted playlist entry, or None.

    Flat extraction sometimes returns a bare video ID rather than a full URL
    for some sites. When that happens, try to reconstruct a real URL from the
    ID for extractors we recognise instead of silently dropping the entry.
    """
    entry_url = entry.get("url") or entry.get("webpage_url")
    if entry_url and is_valid_url(entry_url):
        return entry_url

    ie_key = entry.get("ie_key") or entry.get("extractor_key") or entry.get("extractor")
    entry_id = entry.get("id")
    if ie_key and entry_id:
        template = KNOWN_ENTRY_URL_TEMPLATES.get(ie_key)
        if template:
            return template.format(id=entry_id)

    return None


def get_video_info(url: str) -> dict:
    """Return lightweight information for the preview panel without downloading.

    If the URL points at a playlist, returns {"is_playlist": True, "playlist_title": ...,
    "entries": [{"url": ..., "title": ...}, ...], "unresolved_count": N} using yt-dlp's
    flat extraction, which is fast even for large playlists since it doesn't fetch full
    metadata per video. "unresolved_count" reports how many entries could not be turned
    into a usable URL, so callers can surface that instead of silently losing videos.
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
        unresolved_count = 0
        for entry in info.get("entries") or []:
            if not entry:
                continue
            resolved_url = _resolve_entry_url(entry)
            if not resolved_url:
                unresolved_count += 1
                continue
            entries.append({
                "url": resolved_url,
                "title": entry.get("title") or entry.get("id") or "Video",
            })
        return {
            "is_playlist": True,
            "playlist_title": info.get("title") or "Playlist",
            "entries": entries,
            "unresolved_count": unresolved_count,
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
    if cancel_event is not None and cancel_event.is_set():
        raise DownloadCancelled()

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
                "eta": f"{eta // 60:02d}:{eta % 60:02d}" if eta is not None else "-",
            })
        elif data["status"] == "finished":
            progress_callback({"status": "finished", "percent": 100.0})

    output_template = str(Path(output_dir) / "%(title)s.%(ext)s")
    if duplicate_mode == "Ask me":
        # Use the same format selector we're about to download with, so the
        # probed filename's extension matches what the real download will
        # produce (e.g. mp4 forced for "1080p" vs. a site's native container).
        probe_options = {
            "format": format_selector,
            "outtmpl": output_template,
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
        }
        with yt_dlp.YoutubeDL(probe_options) as probe:
            probe_info = probe.extract_info(url, download=False)
            existing_path = Path(probe.prepare_filename(probe_info))
        if is_audio:
            existing_path = existing_path.with_suffix(".mp3")
        if cancel_event is not None and cancel_event.is_set():
            raise DownloadCancelled()
        if existing_path.exists():
            action = duplicate_callback(str(existing_path)) if duplicate_callback else "skip"
            if action == "skip":
                raise DownloadSkipped(f"Skipped because this file already exists: {existing_path.name}")
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

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filepath = ydl.prepare_filename(info)
    except DownloadCancelled:
        raise
    except yt_dlp.utils.DownloadError as exc:
        # yt-dlp may wrap the hook's raised DownloadCancelled in its own
        # DownloadError rather than letting it propagate unchanged. Treat
        # that the same as a clean cancellation instead of a real failure.
        if cancel_event is not None and cancel_event.is_set():
            raise DownloadCancelled() from exc
        raise

    if is_audio:
        final_path = str(Path(filepath).with_suffix(".mp3"))
    else:
        mp4_path = str(Path(filepath).with_suffix(".mp4"))
        final_path = mp4_path if Path(mp4_path).exists() else filepath
    if not Path(final_path).exists():
        final_path = filepath
    return DownloadResult(filepath=final_path, title=info.get("title", "video"))
