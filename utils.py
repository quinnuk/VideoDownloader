"""
utils.py
--------
Small constants shared across the UI layer. Kept separate from ui.py so
other modules (and any future dialog helpers) can use the same palette
without importing the whole application window.
"""

# Custom palette: lifted charcoal background (instead of near-black) with a
# teal accent, kept distinct from the amber "Pause" and red "danger" colors
# used for status/action buttons so they stay easy to tell apart.
COLOR_BG = "#1c1c1e"
COLOR_PANEL = "#26262a"
COLOR_ACCENT = "#0f6e56"
COLOR_ACCENT_HOVER = "#0c5744"
COLOR_DANGER = "#8a3b34"
COLOR_DANGER_HOVER = "#6f2f2a"

REPO_URL = "https://github.com/quinnuk/VideoDownloader"
