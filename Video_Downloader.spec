# -*- mode: python ; coding: utf-8 -*-
import os
import shutil
from PyInstaller.utils.hooks import collect_all

# FFmpeg to bundle into the .exe. Set FFMPEG_PATH in the environment to
# pin an exact copy (recommended for CI); otherwise this falls back to
# whatever "ffmpeg" resolves to on the current machine's PATH, so the
# build doesn't depend on any one developer's local install location.
FFMPEG_PATH = os.environ.get("FFMPEG_PATH") or shutil.which("ffmpeg")
if not FFMPEG_PATH:
    raise SystemExit(
        "Could not find FFmpeg. Install it and make sure 'ffmpeg' is on "
        "PATH, or set the FFMPEG_PATH environment variable to its exe."
    )

datas = []
binaries = [(FFMPEG_PATH, '.')]
hiddenimports = []
tmp_ret = collect_all('customtkinter')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('yt_dlp')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Video Downloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['video_downloader_icon.ico'],
)
