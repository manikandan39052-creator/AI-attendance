"""
FaceAttend AI Pro - Main Application Entrypoint
AI Powered Smart Face Recognition Attendance Management System
"""

import sys
import os
import config
from core.database import DatabaseManager
from core.logger import log_info, log_error
from ui.app import MainApplication

def main():
    """Application main startup function."""
    try:
        # Initialize directories
        config.init_directories()
        log_info(f"Launching {config.APP_NAME} v{config.APP_VERSION}...")

        # Initialize Database Manager
        db = DatabaseManager()

        # Start CustomTkinter GUI Loop
        app = MainApplication(db)
        app.mainloop()

    except Exception as e:
        log_error(f"Fatal error during application lifecycle: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
