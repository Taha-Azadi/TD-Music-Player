"""
TD Music Player - Configuration Manager
=======================================
JSON-based persistent settings.
"""

import os
import json

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".td_music")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")

DEFAULTS = {
    "volume": 0.7,
    "shuffle": False,
    "repeat": 0,
    "theme": "dark",
    "accent_color": "#1DB954",
    "last_folder": "",
    "music_folders": [],
    "crossfade": 0,
    "playback_speed": 1.0,
    "show_visualizer": True,
    "window_geometry": "1300x850",
    "mini_player": False,
    "language": "en",
    "auto_scan": True,
    "scan_on_startup": False,
    "notification_enabled": True,
    "media_keys_enabled": True,
}

class Settings:
    def __init__(self):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        self._data = {}
        self.load()

    def load(self):
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            except Exception:
                self._data = DEFAULTS.copy()
        else:
            self._data = DEFAULTS.copy()
            self.save()

    def save(self):
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)

    def get(self, key, default=None):
        return self._data.get(key, default)

    def set(self, key, value):
        self._data[key] = value
        self.save()

    def add_music_folder(self, path):
        folders = self.get("music_folders", [])
        if path not in folders:
            folders.append(path)
            self.set("music_folders", folders)

    def remove_music_folder(self, path):
        folders = self.get("music_folders", [])
        if path in folders:
            folders.remove(path)
            self.set("music_folders", folders)
