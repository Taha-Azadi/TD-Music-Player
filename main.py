#!/usr/bin/env python3
"""
TD Music Player v1.0.0
========================
Entry point for the application.

GitHub: https://github.com/Taha-Azadi/TD-Music-Player
Install: pip install -e .
Run: python main.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from td_music_player.main import main

if __name__ == "__main__":
    main()
