"""
TD Music Player - Database Layer
=================================
SQLite3 backend for persistent library storage.
"""

import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.expanduser("~"), ".td_music", "library.db")

class Database:
    """Persistent SQLite database for music library."""

    def __init__(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self._init_tables()

    def _init_tables(self):
        self.cursor.executescript("""
            CREATE TABLE IF NOT EXISTS tracks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filepath TEXT UNIQUE NOT NULL,
                title TEXT,
                artist TEXT,
                album TEXT,
                genre TEXT,
                year TEXT,
                duration INTEGER DEFAULT 0,
                bitrate INTEGER DEFAULT 0,
                play_count INTEGER DEFAULT 0,
                skip_count INTEGER DEFAULT 0,
                rating INTEGER DEFAULT 0,
                is_favorite INTEGER DEFAULT 0,
                last_played TIMESTAMP,
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                track_id INTEGER NOT NULL,
                played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                duration_played INTEGER DEFAULT 0,
                FOREIGN KEY (track_id) REFERENCES tracks(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS playlists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS playlist_tracks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                playlist_id INTEGER NOT NULL,
                track_id INTEGER NOT NULL,
                position INTEGER DEFAULT 0,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (playlist_id) REFERENCES playlists(id) ON DELETE CASCADE,
                FOREIGN KEY (track_id) REFERENCES tracks(id) ON DELETE CASCADE,
                UNIQUE(playlist_id, track_id)
            );

            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_tracks_filepath ON tracks(filepath);
            CREATE INDEX IF NOT EXISTS idx_tracks_artist ON tracks(artist);
            CREATE INDEX IF NOT EXISTS idx_tracks_album ON tracks(album);
            CREATE INDEX IF NOT EXISTS idx_history_played ON history(played_at);
            CREATE INDEX IF NOT EXISTS idx_playlist_tracks ON playlist_tracks(playlist_id);
        """)
        self.conn.commit()

    def add_track(self, filepath, title, artist, album, genre="", year="", duration=0, bitrate=0):
        self.cursor.execute("""
            INSERT OR REPLACE INTO tracks 
            (filepath, title, artist, album, genre, year, duration, bitrate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (filepath, title, artist, album, genre, year, duration, bitrate))
        self.conn.commit()
        return self.get_track_id(filepath)

    def get_track_id(self, filepath):
        self.cursor.execute("SELECT id FROM tracks WHERE filepath=?", (filepath,))
        row = self.cursor.fetchone()
        return row["id"] if row else None

    def get_track(self, filepath):
        self.cursor.execute("SELECT * FROM tracks WHERE filepath=?", (filepath,))
        return dict(self.cursor.fetchone()) if self.cursor.fetchone else None

    def get_all_tracks(self, order_by="title"):
        self.cursor.execute(f"SELECT * FROM tracks ORDER BY {order_by}")
        return [dict(row) for row in self.cursor.fetchall()]

    def search_tracks(self, query):
        q = f"%{query}%"
        self.cursor.execute("""
            SELECT * FROM tracks 
            WHERE title LIKE ? OR artist LIKE ? OR album LIKE ?
            ORDER BY title
        """, (q, q, q))
        return [dict(row) for row in self.cursor.fetchall()]

    def increment_play_count(self, filepath):
        self.cursor.execute("""
            UPDATE tracks 
            SET play_count = play_count + 1, last_played = CURRENT_TIMESTAMP
            WHERE filepath=?
        """, (filepath,))
        self.conn.commit()

    def log_history(self, filepath, duration_played=0):
        track_id = self.get_track_id(filepath)
        if track_id:
            self.cursor.execute("""
                INSERT INTO history (track_id, duration_played)
                VALUES (?, ?)
            """, (track_id, duration_played))
            self.conn.commit()

    def toggle_favorite(self, filepath):
        self.cursor.execute("""
            UPDATE tracks SET is_favorite = NOT is_favorite WHERE filepath=?
        """, (filepath,))
        self.conn.commit()

    def is_favorite(self, filepath):
        self.cursor.execute("SELECT is_favorite FROM tracks WHERE filepath=?", (filepath,))
        row = self.cursor.fetchone()
        return bool(row["is_favorite"]) if row else False

    def get_favorites(self):
        self.cursor.execute("SELECT * FROM tracks WHERE is_favorite=1 ORDER BY title")
        return [dict(row) for row in self.cursor.fetchall()]

    def get_history(self, limit=100):
        self.cursor.execute("""
            SELECT t.*, h.played_at, h.duration_played 
            FROM history h
            JOIN tracks t ON h.track_id = t.id
            ORDER BY h.played_at DESC
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in self.cursor.fetchall()]

    def get_most_played(self, limit=20):
        self.cursor.execute("""
            SELECT * FROM tracks WHERE play_count > 0
            ORDER BY play_count DESC LIMIT ?
        """, (limit,))
        return [dict(row) for row in self.cursor.fetchall()]

    def get_recently_added(self, limit=20):
        self.cursor.execute("""
            SELECT * FROM tracks ORDER BY added_date DESC LIMIT ?
        """, (limit,))
        return [dict(row) for row in self.cursor.fetchall()]

    def get_statistics(self):
        self.cursor.execute("SELECT COUNT(*), SUM(play_count), SUM(duration), SUM(duration * play_count) FROM tracks")
        total_tracks, total_plays, total_duration, total_listened = self.cursor.fetchone()
        self.cursor.execute("SELECT COUNT(*) FROM tracks WHERE is_favorite=1")
        favorites = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT COUNT(*) FROM history")
        history_count = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT COUNT(*) FROM playlists")
        playlist_count = self.cursor.fetchone()[0]
        return {
            "total_tracks": total_tracks or 0,
            "total_plays": total_plays or 0,
            "total_duration": total_duration or 0,
            "total_listened": total_listened or 0,
            "favorites": favorites or 0,
            "history_count": history_count or 0,
            "playlists": playlist_count or 0
        }

    # Playlist management
    def create_playlist(self, name, description=""):
        try:
            self.cursor.execute("INSERT INTO playlists (name, description) VALUES (?, ?)", (name, description))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            return None

    def get_playlists(self):
        self.cursor.execute("SELECT * FROM playlists ORDER BY updated_at DESC")
        return [dict(row) for row in self.cursor.fetchall()]

    def add_to_playlist(self, playlist_id, track_id, position=0):
        self.cursor.execute("""
            INSERT OR IGNORE INTO playlist_tracks (playlist_id, track_id, position)
            VALUES (?, ?, ?)
        """, (playlist_id, track_id, position))
        self.conn.commit()

    def get_playlist_tracks(self, playlist_id):
        self.cursor.execute("""
            SELECT t.* FROM playlist_tracks pt
            JOIN tracks t ON pt.track_id = t.id
            WHERE pt.playlist_id = ?
            ORDER BY pt.position
        """, (playlist_id,))
        return [dict(row) for row in self.cursor.fetchall()]

    def delete_playlist(self, playlist_id):
        self.cursor.execute("DELETE FROM playlists WHERE id=?", (playlist_id,))
        self.conn.commit()

    def save_setting(self, key, value):
        self.cursor.execute("INSERT OR REPLACE INTO settings (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
                          (key, json.dumps(value)))
        self.conn.commit()

    def get_setting(self, key, default=None):
        self.cursor.execute("SELECT value FROM settings WHERE key=?", (key,))
        row = self.cursor.fetchone()
        return json.loads(row["value"]) if row else default

    def close(self):
        self.conn.close()
