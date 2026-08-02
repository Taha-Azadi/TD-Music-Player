"""
TD Music Player - Logging System
=================================
"""

import os
import logging
from datetime import datetime

LOG_DIR = os.path.join(os.path.expanduser("~"), ".td_music")
LOG_PATH = os.path.join(LOG_DIR, "td_music.log")

os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

log = logging.getLogger("TD_Music")
