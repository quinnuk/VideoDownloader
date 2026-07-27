"""
settings.py
-----------
Loads and saves persistent user settings to a JSON file in the user's
AppData folder.
"""

import json
import os
from pathlib import Path

APP_NAME = "VideoDownloader"

DEFAULTS = {
    "output_folder": str(Path.home() / "Videos" / "Downloads"),
    "quality": "best",  # "best" | "1080p" | "audio_only"
    "delete_temp_on_error": True,
    "open_folder_when_finished": True,
    "last_url": "",
}


def _settings_path() -> Path:
    appdata = os.environ.get("APPDATA")
    if appdata:
        base = Path(appdata) / APP_NAME
    else:
        base = Path.home() / f".{APP_NAME.lower()}"
    base.mkdir(parents=True, exist_ok=True)
    return base / "settings.json"


def load_settings() -> dict:
    path = _settings_path()
    data = dict(DEFAULTS)
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                saved = json.load(f)
            data.update(saved)
        except (json.JSONDecodeError, OSError):
            pass
    return data


def save_settings(settings: dict) -> None:
    path = _settings_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
    except OSError:
        pass
