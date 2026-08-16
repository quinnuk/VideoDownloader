"""
ytdlp_updater.py
----------------
Lets the app update its bundled yt-dlp even when frozen into an .exe,
where there is no pip and the yt_dlp package is baked into the bundle.

How it works: yt-dlp's Python package is pure Python (no compiled
extensions), so instead of pip-installing anything, this downloads the
wheel straight from PyPI, pulls the `yt_dlp/` package folder out of it,
and drops that folder into a writable "override" directory:

    %LOCALAPPDATA%\\VideoDownloader\\ytdlp_update\\yt_dlp\\

main.py inserts that override directory at the very front of sys.path,
before anything imports yt_dlp, so the updated copy silently shadows the
version baked into the frozen exe. Takes effect on next launch (yt_dlp
is already imported and running in the current process, so we don't try
to hot-swap it).
"""

import io
import json
import os
import shutil
import urllib.request
import zipfile
from pathlib import Path

PYPI_JSON_URL = "https://pypi.org/pypi/yt-dlp/json"


def override_dir() -> Path:
    """Writable folder that, once populated, shadows the bundled yt_dlp."""
    base = Path(os.environ.get("LOCALAPPDATA", str(Path.home())))
    return base / "VideoDownloader" / "ytdlp_update"


def get_latest_version_and_wheel_url() -> tuple[str, str] | None:
    """Return (version, wheel_url) for the newest yt-dlp release on PyPI, or None."""
    try:
        with urllib.request.urlopen(PYPI_JSON_URL, timeout=8) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception:  # noqa: BLE001 - any network/parse failure just means "couldn't check"
        return None

    version = data.get("info", {}).get("version")
    if not version:
        return None

    for entry in data.get("urls", []):
        if entry.get("packagetype") == "bdist_wheel":
            return version, entry["url"]
    return None


def download_and_install(wheel_url: str, progress_callback=None) -> Path:
    """
    Download the yt-dlp wheel and extract its yt_dlp/ package folder into
    the override directory, replacing whatever was there before.

    Raises on any failure - the caller is expected to catch and report it.
    """
    if progress_callback:
        progress_callback("Downloading yt-dlp...")

    with urllib.request.urlopen(wheel_url, timeout=30) as response:
        wheel_bytes = response.read()

    if progress_callback:
        progress_callback("Extracting...")

    target = override_dir()
    target.mkdir(parents=True, exist_ok=True)
    final_pkg_dir = target / "yt_dlp"
    tmp_dir = target / "yt_dlp.new"

    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True)

    with zipfile.ZipFile(io.BytesIO(wheel_bytes)) as zf:
        for name in zf.namelist():
            # A wheel's top-level yt_dlp/ folder is what we need; skip the
            # dist-info metadata and anything else bundled in the wheel.
            if name.startswith("yt_dlp/") and not name.endswith("/"):
                relative = Path(name).relative_to("yt_dlp")
                dest = tmp_dir / relative
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(zf.read(name))

    # Swap the new copy in: drop the old override (if any), rename the new
    # one into place. The bundled copy inside the frozen exe is untouched
    # either way - this only ever affects the override folder.
    if final_pkg_dir.exists():
        shutil.rmtree(final_pkg_dir)
    tmp_dir.rename(final_pkg_dir)

    if progress_callback:
        progress_callback("Done.")

    return final_pkg_dir


def installed_override_version() -> str | None:
    """Version string of whatever is currently sitting in the override folder, if any."""
    version_file = override_dir() / "yt_dlp" / "version.py"
    if not version_file.exists():
        return None
    try:
        namespace: dict = {}
        exec(version_file.read_text(encoding="utf-8"), namespace)  # noqa: S102 - trusted, we just wrote this file
        return namespace.get("__version__")
    except Exception:  # noqa: BLE001
        return None


def versions_equal(current: str, latest: str) -> bool:
    """
    Compare two yt-dlp version strings while ignoring zero-padding
    differences, e.g. '2026.07.04' (yt_dlp.version.__version__, which keeps
    the zero-padded date format) vs '2026.7.4' (PyPI's "info.version",
    which is normalized per PEP 440 and drops leading zeros from each
    segment). These represent the same release - a naive `==` comparison
    would report an update as available forever, even right after
    installing the latest version.
    """
    try:
        return [int(part) for part in current.split(".")] == [int(part) for part in latest.split(".")]
    except ValueError:
        # Non-numeric segment (shouldn't normally happen for yt-dlp's
        # date-based versions) - fall back to a plain string comparison.
        return current == latest
