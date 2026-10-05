"""
FaceAttend AI Pro - About & System Diagnostics View
Displays application metadata, system specifications, version info, and diagnostics.
"""

import customtkinter as ctk
import sys
import platform
import cv2
import config

class AboutView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=config.COLOR_BG)

        self._create_widgets()

    def _create_widgets(self):
        card = ctk.CTkFrame(self, width=580, height=520, fg_color=config.COLOR_CARD, corner_radius=16)
        card.place(relx=0.5, rely=0.5, anchor="center")

        # Header Badge
        badge = ctk.CTkLabel(card, text="⚡ FACEATTEND AI PRO", font=(config.FONT_FAMILY, 24, "bold"), text_color=config.COLOR_PRIMARY)
        badge.pack(pady=(35, 5))

        tagline = ctk.CTkLabel(card, text=config.APP_TAGLINE, font=(config.FONT_FAMILY, 12, "italic"), text_color=config.COLOR_TEXT_MUTED)
        tagline.pack(pady=(0, 20))

        ver_lbl = ctk.CTkLabel(card, text=f"Version {config.APP_VERSION} (Enterprise Edition)", font=(config.FONT_FAMILY, 12, "bold"), text_color=config.COLOR_ACCENT)
        ver_lbl.pack(pady=(0, 25))

        # Diagnostics Details Box
        diag_box = ctk.CTkFrame(card, fg_color="#0F172A", corner_radius=10)
        diag_box.pack(fill="x", padx=35, pady=10)

        diagnostics = [
            ("Platform Operating System", f"{platform.system()} {platform.release()} ({platform.architecture()[0]})"),
            ("Python Runtime Version", sys.version.split()[0]),
            ("Computer Vision (OpenCV)", cv2.__version__),
            ("GUI Framework", f"CustomTkinter {ctk.__version__}"),
            ("Database Engine", "SQLite3 (PRAGMA WAL Mode Enabled)"),
            ("Target Institutions", "Schools, Colleges, Universities, Enterprise Companies")
        ]

        for k, v in diagnostics:
            row = ctk.CTkFrame(diag_box, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=4)

            k_lbl = ctk.CTkLabel(row, text=f"{k}:", font=(config.FONT_FAMILY, 11, "bold"), text_color=config.COLOR_TEXT_MUTED)
            k_lbl.pack(side="left")

            v_lbl = ctk.CTkLabel(row, text=v, font=(config.FONT_FAMILY, 11, "normal"), text_color=config.COLOR_TEXT_PRIMARY)
            v_lbl.pack(side="right")

        # Footer copyright & license
        copy_lbl = ctk.CTkLabel(
            card,
            text=f"© 2027 {config.COMPANY_NAME}. All Rights Reserved.\nBuilt with Python, CustomTkinter & OpenCV.",
            font=(config.FONT_FAMILY, 10, "normal"),
            text_color=config.COLOR_TEXT_MUTED
        )
        copy_lbl.pack(side="bottom", pady=25)
