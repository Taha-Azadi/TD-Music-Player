"""
TD Music Player - Metadata Extractor
=====================================
Supports: MP3, FLAC, OGG, WAV, M4A, AAC, WMA, OPUS
"""

import os
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from mutagen.wave import WAVE
from mutagen.mp4 import MP4
from mutagen.asf import ASF
from mutagen import File


def get_metadata(filepath):
    meta = {
        "filepath": filepath,
        "title": os.path.splitext(os.path.basename(filepath))[0],
        "artist": "Unknown Artist",
        "album": "Unknown Album",
        "genre": "",
        "year": "",
        "duration": 0,
        "bitrate": 0,
        "cover_data": None,
    }

    try:
        audio = File(filepath)
        if audio is None:
            return meta

        if hasattr(audio, "info") and audio.info:
            meta["duration"] = int(audio.info.length)
            meta["bitrate"] = getattr(audio.info, "bitrate", 0)

        if isinstance(audio, MP3):
            if audio.tags:
                meta["title"] = str(audio.tags.get("TIT2", meta["title"]))
                meta["artist"] = str(audio.tags.get("TPE1", "Unknown Artist"))
                meta["album"] = str(audio.tags.get("TALB", "Unknown Album"))
                meta["genre"] = str(audio.tags.get("TCON", ""))
                meta["year"] = str(audio.tags.get("TDRC", ""))
                for tag in audio.tags.values():
                    if tag.FrameID == "APIC":
                        meta["cover_data"] = tag.data
                        break

        elif isinstance(audio, FLAC):
            meta["title"] = audio.get("TITLE", [meta["title"]])[0]
            meta["artist"] = audio.get("ARTIST", ["Unknown Artist"])[0]
            meta["album"] = audio.get("ALBUM", ["Unknown Album"])[0]
            meta["genre"] = audio.get("GENRE", [""])[0]
            meta["year"] = audio.get("DATE", [""])[0]
            if audio.pictures:
                meta["cover_data"] = audio.pictures[0].data

        elif isinstance(audio, OggVorbis):
            meta["title"] = audio.get("TITLE", [meta["title"]])[0]
            meta["artist"] = audio.get("ARTIST", ["Unknown Artist"])[0]
            meta["album"] = audio.get("ALBUM", ["Unknown Album"])[0]
            meta["genre"] = audio.get("GENRE", [""])[0]
            meta["year"] = audio.get("DATE", [""])[0]

        elif isinstance(audio, MP4):
            meta["title"] = audio.get("\xa9nam", [meta["title"]])[0]
            meta["artist"] = audio.get("\xa9ART", ["Unknown Artist"])[0]
            meta["album"] = audio.get("\xa9alb", ["Unknown Album"])[0]
            if audio.tags and "covr" in audio.tags:
                cover = audio.tags["covr"][0]
                meta["cover_data"] = cover if isinstance(cover, bytes) else cover.encode()

        elif isinstance(audio, ASF):
            meta["title"] = str(audio.get("Title", [meta["title"]])[0])
            meta["artist"] = str(audio.get("Author", ["Unknown Artist"])[0])

    except Exception:
        pass

    return meta


def is_audio_file(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    return ext in (".mp3", ".wav", ".flac", ".ogg", ".wma", ".m4a", ".aac", ".opus", ".mp4")


def format_time(seconds):
    if seconds is None or seconds < 0:
        return "00:00"
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    if minutes >= 60:
        hours = minutes // 60
        minutes = minutes % 60
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def format_duration(seconds):
    if not seconds:
        return "0:00"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"
