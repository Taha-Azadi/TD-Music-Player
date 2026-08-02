"""
TD Music Player - Dynamic Theme Manager
========================================
"""

from PIL import Image
from td_music_player.utils.helpers import extract_dominant_color, adjust_color


class ThemeManager:
    def __init__(self):
        self.base = {
            "bg": "#121212",
            "sidebar": "#000000",
            "card": "#181818",
            "card_hover": "#282828",
            "text": "#FFFFFF",
            "text_secondary": "#B3B3B3",
            "border": "#282828"
        }
        self.accent = "#1DB954"
        self.accent_hover = "#1ED760"
        self.dynamic_bg = "#121212"

    def extract_from_cover(self, cover_data):
        if not cover_data:
            self.accent = "#1DB954"
            self.accent_hover = "#1ED760"
            self.dynamic_bg = "#121212"
            return
        try:
            import io
            img = Image.open(io.BytesIO(cover_data))
            rgb = extract_dominant_color(img)
            self.accent = f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
            self.accent_hover = adjust_color(rgb, 1.3)
            dark = tuple(int(c * 0.15) for c in rgb)
            self.dynamic_bg = f"#{dark[0]:02x}{dark[1]:02x}{dark[2]:02x}"
        except Exception:
            self.accent = "#1DB954"
            self.accent_hover = "#1ED760"
            self.dynamic_bg = "#121212"

    def get_colors(self):
        return {**self.base, "accent": self.accent, "accent_hover": self.accent_hover, "dynamic_bg": self.dynamic_bg}
