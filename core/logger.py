"""
FaceAttend AI Pro - Logging Module
Handles system logging to file and GUI terminal views.
"""

import logging
import os
from datetime import datetime
import config

# Configure root logger
logger = logging.getLogger("FaceAttendAI")
logger.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter(
    '[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# File Handler
file_handler = logging.FileHandler(config.LOG_FILE_PATH, encoding='utf-8')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)

# Stream Handler (Console)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)

if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

def log_info(msg: str):
    logger.info(msg)

def log_warning(msg: str):
    logger.warning(msg)

def log_error(msg: str, exc_info=False):
    logger.error(msg, exc_info=exc_info)

def get_recent_logs(lines_count: int = 100) -> list[str]:
    """Retrieve the last N lines from the log file for GUI display."""
    if not os.path.exists(config.LOG_FILE_PATH):
        return ["No log file found."]
    try:
        with open(config.LOG_FILE_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
            return lines[-lines_count:]
    except Exception as e:
        return [f"Error reading log file: {e}"]
