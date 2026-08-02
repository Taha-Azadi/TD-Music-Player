"""
TD Music Player - Audio Visualizer
====================================
Canvas-based spectrum visualization.
"""

import tkinter as tk
import random
import math
import time


class AudioVisualizer(tk.Canvas):
    def __init__(self, parent, width=500, height=100, bar_count=50, **kwargs):
        super().__init__(parent, width=width, height=height, bg="#121212",
                        highlightthickness=0, **kwargs)
        self.bar_count = bar_count
        self.bar_width = width / bar_count
        self.bars = []
        self.heights = [0] * bar_count
        self.target_heights = [0] * bar_count
        self.accent_color = "#1DB954"
        self._create_bars()
        self._animate()

    def _create_bars(self):
        self.delete("all")
        self.bars = []
        for i in range(self.bar_count):
            x = i * self.bar_width + 1
            bar = self.create_rectangle(
                x, self.winfo_height(), x + self.bar_width - 2, self.winfo_height(),
                fill=self.accent_color, outline=""
            )
            self.bars.append(bar)

    def set_accent(self, color):
        self.accent_color = color
        for bar in self.bars:
            self.itemconfig(bar, fill=color)

    def update_data(self, intensity=1.0):
        h = self.winfo_height()
        random.seed(hash(time.time()) % 1000)
        for i in range(self.bar_count):
            center = self.bar_count / 2
            dist = abs(i - center) / center
            base = random.uniform(0.1, 0.8) * (1 - dist * 0.5)
            self.target_heights[i] = base * h * intensity

    def _animate(self):
        h = self.winfo_height()
        for i, bar in enumerate(self.bars):
            self.heights[i] += (self.target_heights[i] - self.heights[i]) * 0.2
            height = max(2, self.heights[i])
            x = i * self.bar_width + 1
            self.coords(bar, x, h - height, x + self.bar_width - 2, h)
        self.after(30, self._animate)

    def set_active(self, active):
        if not active:
            self.target_heights = [0] * self.bar_count
