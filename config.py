"""
FaceAttend AI Pro - Central Configuration Module
Contains system constants, theme colors, directory paths, and default configurations.
"""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
DATASET_DIR = BASE_DIR / "dataset"
TRAINER_DIR = BASE_DIR / "trainer"
ATTENDANCE_DIR = BASE_DIR / "attendance"
REPORTS_DIR = BASE_DIR / "reports"
EXPORTS_DIR = BASE_DIR / "exports"
LOGS_DIR = BASE_DIR / "logs"
BACKUPS_DIR = BASE_DIR / "backups"
ASSETS_DIR = BASE_DIR / "assets"
DATABASE_DIR = BASE_DIR / "database"
UNKNOWN_DIR = DATASET_DIR / "unknown"

# File Paths
DATABASE_PATH = DATABASE_DIR / "students.db"
MODEL_PATH = TRAINER_DIR / "face_model.pkl"
EXCEL_PATH = ATTENDANCE_DIR / "Attendance.xlsx"
LOG_FILE_PATH = LOGS_DIR / "app.log"

# Application Metadata
APP_NAME = "FaceAttend AI Pro"
APP_VERSION = "2.5.0"
APP_TAGLINE = "AI Powered Smart Face Recognition Attendance Management System"
COMPANY_NAME = "Apex AI Systems"

# UI Theme: Dark Cyber Blue Palette
THEME_MODE = "dark"
THEME_COLOR_SCHEME = "blue"

COLOR_BG = "#0F172A"             # Slate 900
COLOR_SIDEBAR = "#1E293B"        # Slate 800
COLOR_CARD = "#1E293B"           # Slate 800
COLOR_CARD_HOVER = "#334155"     # Slate 700
COLOR_PRIMARY = "#3B82F6"        # Blue 500
COLOR_PRIMARY_HOVER = "#2563EB"  # Blue 600
COLOR_ACCENT = "#06B6D4"         # Cyan 500
COLOR_SUCCESS = "#10B981"        # Emerald 500
COLOR_WARNING = "#F59E0B"        # Amber 500
COLOR_DANGER = "#EF4444"         # Red 500
COLOR_TEXT_PRIMARY = "#F8FAFC"   # Slate 50
COLOR_TEXT_MUTED = "#94A3B8"     # Slate 400
COLOR_BORDER = "#334155"         # Slate 700
COLOR_CANVAS_BG = "#0B1329"      # Deep Cyber Slate

# Typography Fonts
FONT_FAMILY = "Segoe UI"
FONT_TITLE = (FONT_FAMILY, 20, "bold")
FONT_HEADING = (FONT_FAMILY, 16, "bold")
FONT_SUBHEADING = (FONT_FAMILY, 14, "bold")
FONT_BODY = (FONT_FAMILY, 12, "normal")
FONT_BODY_BOLD = (FONT_FAMILY, 12, "bold")
FONT_CAPTION = (FONT_FAMILY, 10, "normal")

# Default Recognition Settings
DEFAULT_CAMERA_INDEX = 0
DEFAULT_CONFIDENCE_THRESHOLD = 0.60  # 60% match required
DEFAULT_DATASET_SAMPLE_COUNT = 100
MIN_QUALITY_BRIGHTNESS = 40.0
MIN_QUALITY_BLUR_VAR = 50.0

# Attendance Time Windows (Default 24h format HH:MM)
DEFAULT_ATTENDANCE_START = "08:00"
DEFAULT_LATE_THRESHOLD = "09:15"
DEFAULT_ATTENDANCE_END = "18:00"

# Defaults
DEFAULT_VOICE_ENABLED = True
DEFAULT_LIVENESS_CHECK = True
DEFAULT_AUTO_BACKUP = True

def init_directories():
    """Ensure all required application directories exist on startup."""
    dirs = [
        DATASET_DIR,
        TRAINER_DIR,
        ATTENDANCE_DIR,
        REPORTS_DIR,
        EXPORTS_DIR,
        LOGS_DIR,
        BACKUPS_DIR,
        ASSETS_DIR,
        DATABASE_DIR,
        UNKNOWN_DIR,
        ASSETS_DIR / "icons",
        ASSETS_DIR / "images",
        ASSETS_DIR / "sounds"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

# Run initialization on import
init_directories()
