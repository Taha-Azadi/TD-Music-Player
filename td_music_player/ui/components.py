"""
TD Music Player - UI Components
================================
Reusable widgets for the application.
"""

import tkinter as tk
import customtkinter as ctk


class IconButton(ctk.CTkButton):
    def __init__(self, parent, image, command, size=40, **kwargs):
        super().__init__(
            parent, text="", image=image, command=command,
            width=size, height=size, fg_color="transparent",
            hover_color="#282828", corner_radius=size//2,
            **kwargs
        )


class PlayButton(ctk.CTkButton):
    def __init__(self, parent, image, command, size=64, accent="#1DB954", **kwargs):
        super().__init__(
            parent, text="", image=image, command=command,
            width=size, height=size, fg_color=accent,
            hover_color="#1ED760", corner_radius=size//2,
            **kwargs
        )


class TrackListbox(tk.Listbox):
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent, bg="#000000", fg="#B3B3B3",
            selectbackground="#282828", selectforeground="#FFFFFF",
            borderwidth=0, highlightthickness=0,
            font=("Segoe UI", 11), activestyle="none",
            selectmode="single", **kwargs
        )


class ProgressBar(ctk.CTkSlider):
    def __init__(self, parent, command=None, **kwargs):
        super().__init__(
            parent, from_=0, to=100, number_of_steps=1000,
            height=6, fg_color="#282828", progress_color="#1DB954",
            button_color="#FFFFFF", button_hover_color="#1ED760",
            button_corner_radius=3, command=command, **kwargs
        )

    def set_accent(self, color):
        self.configure(progress_color=color, button_hover_color=color)


class VolumeSlider(ctk.CTkSlider):
    def __init__(self, parent, command=None, **kwargs):
        super().__init__(
            parent, from_=0, to=1, number_of_steps=100,
            width=120, height=6, fg_color="#282828",
            progress_color="#FFFFFF", button_color="#FFFFFF",
            button_hover_color="#FFFFFF", command=command, **kwargs
        )


class SearchEntry(ctk.CTkEntry):
    def __init__(self, parent, placeholder="Search...", **kwargs):
        super().__init__(
            parent, placeholder_text=placeholder, height=40,
            corner_radius=8, border_width=0, fg_color="#242424",
            text_color="#FFFFFF", placeholder_text_color="#6A6A6A",
            font=ctk.CTkFont(size=13), **kwargs
        )


class TabButton(ctk.CTkButton):
    def __init__(self, parent, text, command, active=False, **kwargs):
        fg = "#282828" if active else "transparent"
        super().__init__(
            parent, text=text, command=command,
            fg_color=fg, hover_color="#282828",
            text_color="#FFFFFF" if active else "#B3B3B3",
            font=ctk.CTkFont(size=13, weight="bold" if active else "normal"),
            height=36, corner_radius=6, anchor="w",
            **kwargs
        )

    def set_active(self, active):
        self.configure(
            fg_color="#282828" if active else "transparent",
            text_color="#FFFFFF" if active else "#B3B3B3",
            font=ctk.CTkFont(size=13, weight="bold" if active else "normal")
        )


class ToastNotification(ctk.CTkToplevel):
    def __init__(self, parent, message, duration=2000, **kwargs):
        super().__init__(parent, **kwargs)
        self.overrideredirect(True)
        self.configure(fg_color="#282828")
        label = ctk.CTkLabel(self, text=message, font=ctk.CTkFont(size=12), text_color="white")
        label.pack(padx=20, pady=10)
        self.update_idletasks()
        x = parent.winfo_x() + parent.winfo_width() - self.winfo_width() - 20
        y = parent.winfo_y() + parent.winfo_height() - self.winfo_height() - 100
        self.geometry(f"+{x}+{y}")
        self.after(duration, self.destroy)
