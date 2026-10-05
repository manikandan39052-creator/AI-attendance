"""
FaceAttend AI Pro - PyInstaller EXE Packaging Automation Script
Builds a standalone executable for Windows platform.
"""

import os
import subprocess
import sys
import shutil

def build_exe():
    print("=" * 60)
    print("      FaceAttend AI Pro - Standalone EXE Packaging")
    print("=" * 60)

    # PyInstaller command list
    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name=FaceAttend_AI_Pro",
        "--add-data=assets;assets",
        "--add-data=config.py;.",
        "main.py"
    ]

    print(f"Executing build command: {' '.join(cmd)}\n")

    try:
        res = subprocess.run(cmd, check=True)
        if res.returncode == 0:
            print("\n" + "=" * 60)
            print("  BUILD SUCCESSFUL! Standalone EXE generated in:")
            print(f"  {os.path.abspath('dist/FaceAttend_AI_Pro/FaceAttend_AI_Pro.exe')}")
            print("=" * 60)
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] PyInstaller build failed: {e}")
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")

if __name__ == "__main__":
    build_exe()
