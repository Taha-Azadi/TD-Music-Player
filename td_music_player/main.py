"""
TD Music Player v1.0.0 - Main Application
=========================================
GitHub: https://github.com/Taha-Azadi/TD-Music-Player
"""

import os
import sys
import io
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import customtkinter as ctk
from PIL import Image
import threading

from td_music_player.music_player import MusicPlayer
from td_music_player.core.database import Database
from td_music_player.core.settings import Settings
from td_music_player.core.logger import log
from td_music_player.ui.theme_manager import ThemeManager
from td_music_player.ui.visualizer import AudioVisualizer
from td_music_player.ui.lyrics_viewer import LyricsViewer
from td_music_player.ui.components import (
    IconButton, PlayButton, TrackListbox, ProgressBar,
    VolumeSlider, SearchEntry, TabButton, ToastNotification
)
from td_music_player.utils.metadata import get_metadata, is_audio_file, format_time
from td_music_player.utils.image_gen import check_and_generate, get_asset_path

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")


class TDMusicPlayer(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("TD Music Player v1.0.0")
        self.geometry("1350x900")
        self.minsize(1100, 750)
        self.configure(fg_color="#121212")

        self.db = Database()
        self.settings = Settings()
        self.theme = ThemeManager()
        self.player = MusicPlayer()

        check_and_generate()

        try:
            icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except Exception:
            pass

        self._load_images()

        self.current_tab = "playlist"
        self.current_metadata = None
        self.is_seeking = False
        self.tray_icon = None
        self.lyrics_visible = False

        self.player.add_callback("on_track_change", self.on_track_change)
        self.player.add_callback("on_play", self.on_play)
        self.player.add_callback("on_pause", self.on_pause)
        self.player.add_callback("on_stop", self.on_stop)
        self.player.add_callback("on_position_update", self.on_position_update)
        self.player.add_callback("on_sleep_timer", self.on_sleep_timer_end)

        self.player.set_volume(self.settings.get("volume", 0.7))

        self._build_ui()
        self._setup_keyboard()
        self._setup_system_tray()
        self._load_saved_tracks()
        self._schedule_update()

        log.info("TD Music Player v1.0.0 started")

    def _load_images(self):
        s = (24, 24)
        l = (32, 32)
        def load(name, size=s):
            p = get_asset_path(name)
            return ctk.CTkImage(Image.open(p), size=size) if os.path.exists(p) else None
        self.img_play = load("play.png", l)
        self.img_pause = load("pause.png", l)
        self.img_next = load("next.png", s)
        self.img_prev = load("previous.png", s)
        self.img_search = load("search.png", s)
        self.img_menu = load("maximize.png", s)
        self.img_vol = load("volume.png", s)
        self.img_mute = load("volume_mute.png", s)
        self.img_shuffle = load("shuffle.png", s)
        self.img_repeat = load("repeat.png", s)
        self.img_folder = load("folder.png", s)
        self.img_heart = load("heart.png", s)
        self.img_heart_empty = load("heart_empty.png", s)
        self.img_lyrics = load("lyrics.png", s)
        self.img_timer = load("timer.png", s)
        self.img_speed = load("speed.png", s)
        self.img_eq = load("equalizer.png", s)
        self.img_settings = load("settings.png", s)

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        # SIDEBAR
        self.sidebar = ctk.CTkFrame(self, width=320, fg_color="#000000", corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(7, weight=1)

        ctk.CTkLabel(self.sidebar, text="🎵 TD Music", font=ctk.CTkFont(size=24, weight="bold"),
                     text_color="white").grid(row=0, column=0, pady=(25, 20), padx=20, sticky="w")

        ctk.CTkLabel(self.sidebar, text="v1.0.0", font=ctk.CTkFont(size=11),
                     text_color="#6A6A6A").grid(row=0, column=0, pady=(25, 20), padx=20, sticky="e")

        self.search_entry = SearchEntry(self.sidebar, placeholder="Search library...")
        self.search_entry.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="ew")
        self.search_entry.bind("<KeyRelease>", self._on_search)

        self.tab_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.tab_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        self.tabs = {}
        tab_data = [
            ("playlist", "🎵 Playlist"),
            ("favorites", "❤️ Favorites"),
            ("history", "🕐 History"),
            ("recent", "🆕 Recently Added"),
            ("top", "🔥 Most Played"),
            ("stats", "📊 Statistics")
        ]
        for i, (key, text) in enumerate(tab_data):
            btn = TabButton(self.tab_frame, text=text, command=lambda k=key: self._switch_tab(k))
            btn.grid(row=i, column=0, pady=2, padx=5, sticky="ew")
            self.tabs[key] = btn
        self.tabs["playlist"].set_active(True)

        self.action_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.action_frame.grid(row=3, column=0, padx=15, pady=15, sticky="ew")

        ctk.CTkButton(self.action_frame, text="➕ Add Files", image=self.img_folder,
                     compound="left", fg_color="#242424", hover_color="#333333",
                     text_color="white", height=40, corner_radius=8,
                     command=self.add_files).grid(row=0, column=0, sticky="ew")

        ctk.CTkButton(self.action_frame, text="📁 Add Folder", image=self.img_folder,
                     compound="left", fg_color="#242424", hover_color="#333333",
                     text_color="white", height=40, corner_radius=8,
                     command=self.add_folder).grid(row=1, column=0, pady=(8, 0), sticky="ew")

        ctk.CTkButton(self.action_frame, text="💾 New Playlist", image=self.img_settings,
                     compound="left", fg_color="#242424", hover_color="#333333",
                     text_color="white", height=40, corner_radius=8,
                     command=self._create_playlist).grid(row=2, column=0, pady=(8, 0), sticky="ew")

        self.list_container = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.list_container.grid(row=4, column=0, padx=15, pady=10, sticky="nsew")
        self.list_container.grid_rowconfigure(0, weight=1)
        self.list_container.grid_columnconfigure(0, weight=1)

        self.track_list = TrackListbox(self.list_container)
        self.track_list.grid(row=0, column=0, sticky="nsew")
        self.track_list.bind("<Double-Button-1>", self._on_playlist_double_click)
        self.track_list.bind("<Delete>", self._on_playlist_delete)

        scrollbar = ctk.CTkScrollbar(self.list_container, command=self.track_list.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.track_list.configure(yscrollcommand=scrollbar.set)

        self.counter_label = ctk.CTkLabel(self.sidebar, text="0 tracks", font=ctk.CTkFont(size=11),
                                          text_color="#6A6A6A")
        self.counter_label.grid(row=5, column=0, pady=(5, 5), padx=20, sticky="w")

        self.sleep_label = ctk.CTkLabel(self.sidebar, text="", font=ctk.CTkFont(size=11),
                                          text_color="#1DB954")
        self.sleep_label.grid(row=6, column=0, pady=(0, 10), padx=20, sticky="w")

        # MAIN CONTENT
        self.main_frame = ctk.CTkFrame(self, fg_color="#121212", corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.content_frame.grid(row=0, column=0, sticky="nsew", padx=30, pady=30)
        self.content_frame.grid_rowconfigure(1, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        self.top_bar = ctk.CTkFrame(self.content_frame, fg_color="transparent", height=40)
        self.top_bar.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        self.top_bar.grid_columnconfigure(0, weight=1)

        self.view_title = ctk.CTkLabel(self.top_bar, text="Now Playing",
                                       font=ctk.CTkFont(size=28, weight="bold"), text_color="white")
        self.view_title.grid(row=0, column=0, sticky="w")

        self.extra_controls = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        self.extra_controls.grid(row=0, column=1, sticky="e")

        IconButton(self.extra_controls, self.img_lyrics, self._toggle_lyrics, size=36).grid(row=0, column=0, padx=5)
        IconButton(self.extra_controls, self.img_timer, self._set_sleep_timer, size=36).grid(row=0, column=1, padx=5)
        IconButton(self.extra_controls, self.img_speed, self._set_speed, size=36).grid(row=0, column=2, padx=5)
        self.heart_btn = IconButton(self.extra_controls, self.img_heart_empty, self._toggle_favorite, size=36)
        self.heart_btn.grid(row=0, column=3, padx=5)

        self.center_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.center_frame.grid(row=1, column=0, pady=10)

        self.cover_label = ctk.CTkLabel(self.center_frame, text="", width=400, height=400)
        self.cover_label.grid(row=0, column=0)
        self._set_default_cover()

        self.info_frame = ctk.CTkFrame(self.center_frame, fg_color="transparent")
        self.info_frame.grid(row=1, column=0, pady=(20, 10))

        self.track_title = ctk.CTkLabel(self.info_frame, text="No track playing",
                                          font=ctk.CTkFont(size=28, weight="bold"), text_color="white")
        self.track_title.grid(row=0, column=0)

        self.track_artist = ctk.CTkLabel(self.info_frame, text="Select a track to begin",
                                           font=ctk.CTkFont(size=16), text_color="#B3B3B3")
        self.track_artist.grid(row=1, column=0, pady=(5, 0))

        self.track_album = ctk.CTkLabel(self.info_frame, text="",
                                        font=ctk.CTkFont(size=13), text_color="#6A6A6A")
        self.track_album.grid(row=2, column=0, pady=(2, 0))

        self.track_meta = ctk.CTkLabel(self.info_frame, text="",
                                       font=ctk.CTkFont(size=11), text_color="#4A4A4A")
        self.track_meta.grid(row=3, column=0, pady=(2, 0))

        self.visualizer = AudioVisualizer(self.content_frame, width=550, height=100, bar_count=60)
        self.visualizer.grid(row=2, column=0, pady=(20, 10))

        self.lyrics_viewer = LyricsViewer(self.content_frame)
        self.lyrics_viewer.grid(row=1, column=0, sticky="nsew")
        self.lyrics_viewer.grid_remove()

        self.progress_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.progress_frame.grid(row=3, column=0, sticky="ew", pady=(10, 5))
        self.progress_frame.grid_columnconfigure(1, weight=1)

        self.time_current = ctk.CTkLabel(self.progress_frame, text="0:00", font=ctk.CTkFont(size=12),
                                          text_color="#B3B3B3", width=50)
        self.time_current.grid(row=0, column=0, padx=(0, 10))

        self.progress = ProgressBar(self.progress_frame)
        self.progress.grid(row=0, column=1, sticky="ew")
        self.progress.bind("<Button-1>", self._on_seek_start)
        self.progress.bind("<ButtonRelease-1>", self._on_seek_end)

        self.time_total = ctk.CTkLabel(self.progress_frame, text="0:00", font=ctk.CTkFont(size=12),
                                      text_color="#B3B3B3", width=50)
        self.time_total.grid(row=0, column=2, padx=(10, 0))

        # PLAYER BAR
        self.player_bar = ctk.CTkFrame(self, height=100, fg_color="#000000", corner_radius=0)
        self.player_bar.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.player_bar.grid_propagate(False)
        self.player_bar.grid_columnconfigure(0, weight=1)
        self.player_bar.grid_columnconfigure(1, weight=2)
        self.player_bar.grid_columnconfigure(2, weight=1)

        self.mini_info = ctk.CTkFrame(self.player_bar, fg_color="transparent")
        self.mini_info.grid(row=0, column=0, padx=20, sticky="w")

        self.mini_cover = ctk.CTkLabel(self.mini_info, text="", width=56, height=56)
        self.mini_cover.grid(row=0, column=0, rowspan=2)
        self._set_mini_cover_default()

        self.mini_title = ctk.CTkLabel(self.mini_info, text="TD Music Player v1.0.0",
                                       font=ctk.CTkFont(size=13, weight="bold"), text_color="white")
        self.mini_title.grid(row=0, column=1, padx=(12, 0), sticky="sw")

        self.mini_artist = ctk.CTkLabel(self.mini_info, text="Ready to play",
                                          font=ctk.CTkFont(size=11), text_color="#B3B3B3")
        self.mini_artist.grid(row=1, column=1, padx=(12, 0), sticky="nw")

        self.controls = ctk.CTkFrame(self.player_bar, fg_color="transparent")
        self.controls.grid(row=0, column=1)

        self.shuffle_btn = IconButton(self.controls, self.img_shuffle, self.toggle_shuffle, size=36)
        self.shuffle_btn.grid(row=0, column=0, padx=8)

        self.prev_btn = IconButton(self.controls, self.img_prev, self.player.previous_track, size=40)
        self.prev_btn.grid(row=0, column=1, padx=8)

        self.play_btn = PlayButton(self.controls, self.img_play, self.toggle_play, size=64)
        self.play_btn.grid(row=0, column=2, padx=12)

        self.next_btn = IconButton(self.controls, self.img_next, self.player.next_track, size=40)
        self.next_btn.grid(row=0, column=3, padx=8)

        self.repeat_btn = IconButton(self.controls, self.img_repeat, self.toggle_repeat, size=36)
        self.repeat_btn.grid(row=0, column=4, padx=8)

        self.vol_frame = ctk.CTkFrame(self.player_bar, fg_color="transparent")
        self.vol_frame.grid(row=0, column=2, padx=20, sticky="e")

        self.vol_btn = IconButton(self.vol_frame, self.img_vol, self.toggle_mute, size=32)
        self.vol_btn.grid(row=0, column=0)

        self.vol_slider = VolumeSlider(self.vol_frame, command=self._on_volume_change)
        self.vol_slider.grid(row=0, column=1, padx=(8, 0))
        self.vol_slider.set(self.player.get_volume())

        self.is_muted = False
        self.pre_mute_vol = 0.7

    def _set_default_cover(self):
        path = get_asset_path("empty_cover.jpg")
        if os.path.exists(path):
            img = Image.open(path).resize((400, 400), Image.Resampling.LANCZOS)
            self.cover_img = ctk.CTkImage(img, size=(400, 400))
            self.cover_label.configure(image=self.cover_img)
        else:
            self.cover_label.configure(text="🎵", font=ctk.CTkFont(size=150))

    def _set_mini_cover_default(self):
        path = get_asset_path("empty_cover.jpg")
        if os.path.exists(path):
            img = Image.open(path).resize((56, 56), Image.Resampling.LANCZOS)
            self.mini_cover_img = ctk.CTkImage(img, size=(56, 56))
            self.mini_cover.configure(image=self.mini_cover_img)
        else:
            self.mini_cover.configure(text="🎵", font=ctk.CTkFont(size=24))

    def _update_cover(self, cover_data):
        try:
            if cover_data:
                img = Image.open(io.BytesIO(cover_data))
                self.theme.extract_from_cover(cover_data)
                colors = self.theme.get_colors()
                self._apply_dynamic_theme(colors)

                img_big = img.resize((400, 400), Image.Resampling.LANCZOS)
                self.cover_img = ctk.CTkImage(img_big, size=(400, 400))
                self.cover_label.configure(image=self.cover_img)

                img_small = img.resize((56, 56), Image.Resampling.LANCZOS)
                self.mini_cover_img = ctk.CTkImage(img_small, size=(56, 56))
                self.mini_cover.configure(image=self.mini_cover_img)
            else:
                self._set_default_cover()
                self._set_mini_cover_default()
                self._reset_theme()
        except Exception:
            self._set_default_cover()

    def _apply_dynamic_theme(self, colors):
        accent = colors["accent"]
        self.play_btn.configure(fg_color=accent, hover_color=colors["accent_hover"])
        self.progress.set_accent(accent)
        self.visualizer.set_accent(accent)
        self.sleep_label.configure(text_color=accent)

    def _reset_theme(self):
        self.play_btn.configure(fg_color="#1DB954", hover_color="#1ED760")
        self.progress.set_accent("#1DB954")
        self.visualizer.set_accent("#1DB954")

    def toggle_play(self):
        if not self.player.get_playlist():
            self.add_files()
            return
        self.player.pause()

    def toggle_shuffle(self):
        state = self.player.toggle_shuffle()
        if state:
            self.shuffle_btn.configure(fg_color="#1DB954", hover_color="#1ED760")
        else:
            self.shuffle_btn.configure(fg_color="transparent", hover_color="#282828")

    def toggle_repeat(self):
        mode = self.player.set_repeat()
        colors = ["transparent", "#1DB954", "#1DB954"]
        self.repeat_btn.configure(fg_color=colors[mode], hover_color="#1ED760" if mode else "#282828")

    def toggle_mute(self):
        if self.is_muted:
            self.player.set_volume(self.pre_mute_vol)
            self.vol_slider.set(self.pre_mute_vol)
            self.vol_btn.configure(image=self.img_vol)
            self.is_muted = False
        else:
            self.pre_mute_vol = self.player.get_volume()
            self.player.set_volume(0)
            self.vol_slider.set(0)
            self.vol_btn.configure(image=self.img_mute)
            self.is_muted = True

    def _on_volume_change(self, event=None):
        vol = self.vol_slider.get()
        self.player.set_volume(vol)
        self.settings.set("volume", vol)
        if vol > 0 and self.is_muted:
            self.is_muted = False
            self.vol_btn.configure(image=self.img_vol)
        elif vol == 0 and not self.is_muted:
            self.is_muted = True
            self.vol_btn.configure(image=self.img_mute)

    def _on_seek_start(self, event):
        self.is_seeking = True

    def _on_seek_end(self, event):
        self.is_seeking = False
        if self.current_metadata and self.current_metadata.get("duration", 0) > 0:
            pos = self.progress.get() / 100.0 * self.current_metadata["duration"]
            self.player.seek(pos)

    def add_files(self):
        files = filedialog.askopenfilenames(
            title="Select Music Files",
            filetypes=[("Audio", "*.mp3 *.wav *.flac *.ogg *.m4a *.aac *.wma *.opus"),
                       ("All", "*.*")]
        )
        if files:
            self._add_tracks(files)

    def add_folder(self):
        folder = filedialog.askdirectory(title="Select Music Folder")
        if folder:
            self.settings.add_music_folder(folder)
            files = []
            for root, _, filenames in os.walk(folder):
                for f in filenames:
                    fp = os.path.join(root, f)
                    if is_audio_file(fp):
                        files.append(fp)
            if files:
                self._add_tracks(files)
                ToastNotification(self, f"Added {len(files)} tracks")

    def _add_tracks(self, filepaths):
        added = 0
        for fp in filepaths:
            if is_audio_file(fp) and self.player.add_to_playlist(fp):
                meta = get_metadata(fp)
                self.db.add_track(fp, meta["title"], meta["artist"], meta["album"],
                                 meta.get("genre", ""), meta.get("year", ""), meta["duration"], meta.get("bitrate", 0))
                added += 1
        if added > 0:
            self._refresh_list()
            if len(self.player.get_playlist()) == added:
                self.player.play(0)
        log.info(f"Added {added} tracks")

    def _refresh_list(self):
        self.track_list.delete(0, tk.END)
        self._list_mapping = []
        filter_text = self.search_entry.get().lower()

        if self.current_tab == "playlist":
            tracks = [(i, get_metadata(t)) for i, t in enumerate(self.player.get_playlist())]
        elif self.current_tab == "favorites":
            tracks = [(i, t) for i, t in enumerate(self.db.get_favorites())]
        elif self.current_tab == "history":
            tracks = [(i, t) for i, t in enumerate(self.db.get_history(50))]
        elif self.current_tab == "recent":
            tracks = [(i, t) for i, t in enumerate(self.db.get_recently_added(30))]
        elif self.current_tab == "top":
            tracks = [(i, t) for i, t in enumerate(self.db.get_most_played(30))]
        elif self.current_tab == "stats":
            stats = self.db.get_statistics()
            text = f"""📊 TD Music Player Statistics

Total Tracks: {stats['total_tracks']}
Total Plays: {stats['total_plays']}
Favorites: {stats['favorites']}
Playlists: {stats['playlists']}
History Entries: {stats['history_count']}
Total Duration: {format_time(stats['total_duration'])}
Total Listened: {format_time(stats['total_listened'])}
"""
            self.track_list.insert(tk.END, text)
            self.counter_label.configure(text="Statistics")
            return
        else:
            tracks = []

        for idx, meta in tracks:
            text = f"{meta.get('title', 'Unknown')} - {meta.get('artist', 'Unknown')}"
            if not filter_text or filter_text in text.lower():
                self.track_list.insert(tk.END, text)
                self._list_mapping.append(idx)

        self.counter_label.configure(text=f"{len(self.track_list.get(0, tk.END))} tracks")

    def _switch_tab(self, tab):
        for k, btn in self.tabs.items():
            btn.set_active(k == tab)
        self.current_tab = tab
        self._refresh_list()

    def _on_search(self, event=None):
        self._refresh_list()

    def _on_playlist_double_click(self, event):
        if self.current_tab != "playlist":
            return
        sel = self.track_list.curselection()
        if sel:
            idx = self._list_mapping[sel[0]]
            self.player.play(idx)

    def _on_playlist_delete(self, event):
        if self.current_tab != "playlist":
            return
        sel = self.track_list.curselection()
        if sel:
            idx = self._list_mapping[sel[0]]
            self.player.remove_from_playlist(idx)
            self._refresh_list()

    def _create_playlist(self):
        name = simpledialog.askstring("New Playlist", "Enter playlist name:")
        if name:
            pid = self.db.create_playlist(name)
            if pid:
                ToastNotification(self, f"Playlist '{name}' created")
            else:
                messagebox.showwarning("Exists", f"Playlist '{name}' already exists")

    def _load_saved_tracks(self):
        tracks = self.db.get_all_tracks()
        for t in tracks:
            if os.path.exists(t["filepath"]):
                self.player.add_to_playlist(t["filepath"])
        self._refresh_list()

    def _toggle_lyrics(self):
        self.lyrics_visible = not self.lyrics_visible
        if self.lyrics_visible:
            self.lyrics_viewer.grid()
            self.center_frame.grid_remove()
            self.visualizer.grid_remove()
            self._load_lyrics()
        else:
            self.lyrics_viewer.grid_remove()
            self.center_frame.grid()
            self.visualizer.grid()

    def _load_lyrics(self):
        if self.current_metadata:
            filepath = self.current_metadata["filepath"]
            lrc_path = os.path.splitext(filepath)[0] + ".lrc"
            if os.path.exists(lrc_path):
                try:
                    with open(lrc_path, "r", encoding="utf-8") as f:
                        self.lyrics_viewer.set_lyrics(f.read())
                except Exception:
                    self.lyrics_viewer.set_lyrics("")
            else:
                self.lyrics_viewer.set_lyrics("")

    def _set_sleep_timer(self):
        val = simpledialog.askinteger("Sleep Timer", "Minutes (0 = off):", minvalue=0)
        if val is not None:
            if val > 0:
                self.player.set_sleep_timer(val)
                self.sleep_label.configure(text=f"⏲️ Sleep: {val}min")
                ToastNotification(self, f"Sleep timer: {val} min")
            else:
                self.player.set_sleep_timer(0)
                self.sleep_label.configure(text="")

    def on_sleep_timer_end(self):
        self.sleep_label.configure(text="")
        ToastNotification(self, "Sleep timer ended")

    def _set_speed(self):
        val = simpledialog.askfloat("Speed", "Playback speed (0.5 - 2.0):", minvalue=0.5, maxvalue=2.0)
        if val:
            self.player.set_speed(val)
            ToastNotification(self, f"Speed: {val}x")

    def _toggle_favorite(self):
        if self.current_metadata:
            fp = self.current_metadata["filepath"]
            self.db.toggle_favorite(fp)
            is_fav = self.db.is_favorite(fp)
            self.heart_btn.configure(image=self.img_heart if is_fav else self.img_heart_empty)
            if is_fav:
                ToastNotification(self, "Added to favorites ❤️")
            else:
                ToastNotification(self, "Removed from favorites")

    def _setup_keyboard(self):
        self.bind("<space>", lambda e: self.toggle_play())
        self.bind("<Right>", lambda e: self.player.next_track())
        self.bind("<Left>", lambda e: self.player.previous_track())
        self.bind("<Up>", lambda e: self._change_volume(0.05))
        self.bind("<Down>", lambda e: self._change_volume(-0.05))
        self.bind("<m>", lambda e: self.toggle_mute())
        self.bind("<s>", lambda e: self.toggle_shuffle())
        self.bind("<r>", lambda e: self.toggle_repeat())
        self.bind("<l>", lambda e: self._toggle_lyrics())
        self.bind("<f>", lambda e: self._toggle_favorite())
        self.bind("<Control-o>", lambda e: self.add_files())
        self.bind("<Control-q>", lambda e: self.on_closing())
        self.bind("<Control-n>", lambda e: self._create_playlist())

    def _change_volume(self, delta):
        new_vol = max(0.0, min(1.0, self.player.get_volume() + delta))
        self.player.set_volume(new_vol)
        self.vol_slider.set(new_vol)

    def _setup_system_tray(self):
        try:
            import pystray
            icon_path = get_asset_path("icon.png")
            if os.path.exists(icon_path):
                icon_img = Image.open(icon_path)
                menu = pystray.Menu(
                    pystray.MenuItem("Play/Pause", lambda: self.toggle_play()),
                    pystray.MenuItem("Next", lambda: self.player.next_track()),
                    pystray.MenuItem("Previous", lambda: self.player.previous_track()),
                    pystray.MenuItem("Exit", lambda: self.on_closing())
                )
                self.tray_icon = pystray.Icon("TD_Music", icon_img, "TD Music Player", menu)
                threading.Thread(target=self.tray_icon.run, daemon=True).start()
        except ImportError:
            log.info("pystray not installed")

    def on_track_change(self, filepath, index):
        self.current_metadata = get_metadata(filepath)
        self.db.increment_play_count(filepath)
        self.db.log_history(filepath)

        self.track_title.configure(text=self.current_metadata["title"])
        self.track_artist.configure(text=self.current_metadata["artist"])
        self.track_album.configure(text=self.current_metadata.get("album", ""))

        bitrate = self.current_metadata.get("bitrate", 0)
        bitrate_str = f"{bitrate//1000} kbps" if bitrate else ""
        self.track_meta.configure(text=f"{format_time(self.current_metadata['duration'])}  •  {bitrate_str}")

        self.mini_title.configure(text=self.current_metadata["title"][:35])
        self.mini_artist.configure(text=self.current_metadata["artist"][:40])
        self.time_total.configure(text=format_time(self.current_metadata["duration"]))
        self.progress.set(0)

        self._update_cover(self.current_metadata.get("cover_data"))

        is_fav = self.db.is_favorite(filepath)
        self.heart_btn.configure(image=self.img_heart if is_fav else self.img_heart_empty)

        self._highlight_current(index)
        self._load_lyrics()

    def _highlight_current(self, index):
        try:
            for vis_idx, real_idx in enumerate(self._list_mapping):
                if real_idx == index:
                    self.track_list.selection_clear(0, tk.END)
                    self.track_list.selection_set(vis_idx)
                    self.track_list.see(vis_idx)
                    break
        except Exception:
            pass

    def on_play(self, filepath):
        self.play_btn.configure(image=self.img_pause)
        self.visualizer.set_active(True)

    def on_pause(self, filepath):
        self.play_btn.configure(image=self.img_play)
        self.visualizer.set_active(False)

    def on_stop(self):
        self.play_btn.configure(image=self.img_play)
        self.progress.set(0)
        self.time_current.configure(text="0:00")
        self.visualizer.set_active(False)

    def on_position_update(self, position):
        if not self.is_seeking and self.current_metadata:
            duration = self.current_metadata.get("duration", 0)
            if duration > 0:
                progress = (position / duration) * 100
                self.progress.set(progress)
                self.time_current.configure(text=format_time(position))

        if self.player.is_playing():
            self.visualizer.update_data(intensity=0.8)
        else:
            self.visualizer.update_data(intensity=0.1)

        remaining = self.player.get_sleep_remaining()
        if remaining > 0:
            self.sleep_label.configure(text=f"⏲️ {remaining//60}:{remaining%60:02d}")

    def _schedule_update(self):
        self.player.update()
        self.after(200, self._schedule_update)

    def on_closing(self):
        if self.tray_icon:
            self.tray_icon.stop()
        self.settings.set("volume", self.player.get_volume())
        self.db.close()
        self.player.cleanup()
        log.info("TD Music Player v1.0.0 closed")
        self.destroy()


def main():
    app = TDMusicPlayer()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()


if __name__ == "__main__":
    main()
