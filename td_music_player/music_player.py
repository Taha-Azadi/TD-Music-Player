"""
TD Music Player - Advanced Audio Engine
=======================================
Pygame-based audio engine with advanced features.
"""

import os
import random
import time
import pygame
from pygame import mixer


class MusicPlayer:
    REPEAT_OFF = 0
    REPEAT_ALL = 1
    REPEAT_ONE = 2

    def __init__(self):
        mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        self._playlist = []
        self._current_index = -1
        self._is_playing = False
        self._is_paused = False
        self._volume = 0.7
        self._shuffle = False
        self._repeat = self.REPEAT_OFF
        self._speed = 1.0
        self._sleep_end_time = None
        self._history = []
        self._callbacks = {
            "on_track_change": [],
            "on_play": [],
            "on_pause": [],
            "on_stop": [],
            "on_end": [],
            "on_position_update": [],
            "on_sleep_timer": []
        }
        self._position_offset = 0
        self._start_time = 0
        mixer.music.set_endevent(pygame.USEREVENT + 1)

    def add_callback(self, event, callback):
        if event in self._callbacks:
            self._callbacks[event].append(callback)

    def _trigger(self, event, *args):
        for cb in self._callbacks.get(event, []):
            try:
                cb(*args)
            except Exception:
                pass

    def add_to_playlist(self, filepath):
        if os.path.exists(filepath) and filepath not in self._playlist:
            self._playlist.append(filepath)
            return True
        return False

    def add_files(self, filepaths):
        added = 0
        for fp in filepaths:
            if self.add_to_playlist(fp):
                added += 1
        return added

    def remove_from_playlist(self, index):
        if 0 <= index < len(self._playlist):
            was_playing = (index == self._current_index and self._is_playing)
            self._playlist.pop(index)
            if index < self._current_index:
                self._current_index -= 1
            elif index == self._current_index:
                self.stop()
                if self._playlist:
                    self._current_index = min(self._current_index, len(self._playlist) - 1)
                    if was_playing:
                        self.play()
            return True
        return False

    def clear_playlist(self):
        self.stop()
        self._playlist.clear()
        self._current_index = -1
        self._history.clear()

    def get_playlist(self):
        return self._playlist.copy()

    def get_current_track(self):
        if 0 <= self._current_index < len(self._playlist):
            return self._playlist[self._current_index]
        return None

    def get_current_index(self):
        return self._current_index

    def play(self, index=None):
        if not self._playlist:
            return False
        if index is not None:
            if 0 <= index < len(self._playlist):
                self._current_index = index
            else:
                return False
        elif self._current_index == -1:
            self._current_index = 0

        filepath = self._playlist[self._current_index]
        try:
            mixer.music.load(filepath)
            mixer.music.set_volume(self._volume)
            mixer.music.play()
            self._is_playing = True
            self._is_paused = False
            self._start_time = time.time()
            self._position_offset = 0
            self._trigger("on_track_change", filepath, self._current_index)
            self._trigger("on_play", filepath)
            return True
        except Exception:
            return False

    def pause(self):
        if self._is_playing:
            if self._is_paused:
                mixer.music.unpause()
                self._is_paused = False
                self._start_time = time.time() - self._position_offset
                self._trigger("on_play", self.get_current_track())
            else:
                mixer.music.pause()
                self._is_paused = True
                self._position_offset = time.time() - self._start_time
                self._trigger("on_pause", self.get_current_track())

    def stop(self):
        mixer.music.stop()
        self._is_playing = False
        self._is_paused = False
        self._position_offset = 0
        self._trigger("on_stop")

    def next_track(self):
        if not self._playlist:
            return
        if self._repeat == self.REPEAT_ONE:
            self.play(self._current_index)
            return
        if self._shuffle:
            if len(self._playlist) > 1:
                next_idx = random.randint(0, len(self._playlist) - 1)
                while next_idx == self._current_index:
                    next_idx = random.randint(0, len(self._playlist) - 1)
                self._history.append(self._current_index)
                self.play(next_idx)
        else:
            next_idx = self._current_index + 1
            if next_idx >= len(self._playlist):
                if self._repeat == self.REPEAT_ALL:
                    next_idx = 0
                else:
                    self.stop()
                    return
            self.play(next_idx)

    def previous_track(self):
        if not self._playlist:
            return
        if self._repeat == self.REPEAT_ONE:
            self.play(self._current_index)
            return
        if self._shuffle and self._history:
            prev_idx = self._history.pop()
            self.play(prev_idx)
        else:
            prev_idx = self._current_index - 1
            if prev_idx < 0:
                if self._repeat == self.REPEAT_ALL:
                    prev_idx = len(self._playlist) - 1
                else:
                    prev_idx = 0
            self.play(prev_idx)

    def seek(self, position_seconds):
        if self._is_playing:
            try:
                mixer.music.set_pos(position_seconds)
                self._position_offset = position_seconds
                self._start_time = time.time()
            except Exception:
                pass

    def get_position(self):
        if self._is_playing:
            if self._is_paused:
                return self._position_offset
            return time.time() - self._start_time + self._position_offset
        return 0

    def get_volume(self):
        return self._volume

    def set_volume(self, vol):
        self._volume = max(0.0, min(1.0, vol))
        mixer.music.set_volume(self._volume)

    def toggle_shuffle(self):
        self._shuffle = not self._shuffle
        if self._shuffle:
            self._history.clear()
        return self._shuffle

    def is_shuffled(self):
        return self._shuffle

    def set_repeat(self, mode=None):
        if mode is None:
            self._repeat = (self._repeat + 1) % 3
        else:
            self._repeat = mode
        return self._repeat

    def get_repeat(self):
        return self._repeat

    def is_playing(self):
        return self._is_playing and not self._is_paused

    def is_paused(self):
        return self._is_paused

    def set_speed(self, speed):
        self._speed = max(0.5, min(2.0, speed))
        return self._speed

    def get_speed(self):
        return self._speed

    def set_sleep_timer(self, minutes):
        if minutes > 0:
            self._sleep_end_time = time.time() + (minutes * 60)
        else:
            self._sleep_end_time = None

    def get_sleep_remaining(self):
        if self._sleep_end_time:
            remaining = self._sleep_end_time - time.time()
            return max(0, int(remaining))
        return 0

    def update(self):
        if self._is_playing and not self._is_paused:
            if not mixer.music.get_busy():
                self.next_track()
            else:
                self._trigger("on_position_update", self.get_position())
            if self._sleep_end_time and time.time() >= self._sleep_end_time:
                self.stop()
                self._sleep_end_time = None
                self._trigger("on_sleep_timer")

    def cleanup(self):
        mixer.music.stop()
        mixer.quit()
