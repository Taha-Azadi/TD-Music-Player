"""
TD Music Player - Lyrics Viewer
=================================
"""

import tkinter as tk
from tkinter import scrolledtext


class LyricsViewer(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg="#121212", **kwargs)
        self.text_widget = scrolledtext.ScrolledText(
            self, wrap=tk.WORD, font=("Segoe UI", 14),
            bg="#121212", fg="#B3B3B3", bd=0, highlightthickness=0,
            padx=20, pady=20
        )
        self.text_widget.pack(fill=tk.BOTH, expand=True)
        self.text_widget.config(state=tk.DISABLED)

    def set_lyrics(self, text):
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(tk.END, text if text else "No lyrics available.\n\nAdd .lrc file with same name as track.")
        self.text_widget.config(state=tk.DISABLED)

    def clear(self):
        self.set_lyrics("")
