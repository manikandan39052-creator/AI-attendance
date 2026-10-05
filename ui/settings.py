"""
FaceAttend AI Pro - System Settings & Backup Manager View
Camera configuration, confidence threshold slider, shift time windows, voice toggle, and database backup/restore.
"""

import customtkinter as ctk
from typing import Callable
import config
from core.database import DatabaseManager
from core.backup import BackupManager

class SettingsView(ctk.CTkFrame):
    def __init__(self, parent, db: DatabaseManager, show_toast: Callable[[str, str], None]):
        super().__init__(parent, fg_color=config.COLOR_BG)
        self.db = db
        self.show_toast = show_toast
        self.backup_mgr = BackupManager()

        self._create_widgets()
        self.load_settings()
        self.load_backups_list()

    def _create_widgets(self):
        # Header
        header = ctk.CTkFrame(self, fg_color=config.COLOR_CARD, corner_radius=12)
        header.pack(fill="x", padx=15, pady=(15, 10))

        title = ctk.CTkLabel(
            header,
            text="⚙️ SYSTEM CONFIGURATION & BACKUP MANAGEMENT",
            font=(config.FONT_FAMILY, 16, "bold"),
            text_color=config.COLOR_TEXT_PRIMARY
        )
        title.pack(side="left", padx=20, pady=15)

        # Main Scroll Container
        scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # --- SECTION 1: HARDWARE & RECOGNITION SETTINGS ---
        sec1 = ctk.CTkFrame(scroll_container, fg_color=config.COLOR_CARD, corner_radius=12)
        sec1.pack(fill="x", pady=(0, 15))

        s1_title = ctk.CTkLabel(sec1, text="📹 CAMERA & AI RECOGNITION ENGINE", font=(config.FONT_FAMILY, 14, "bold"), text_color=config.COLOR_TEXT_PRIMARY)
        s1_title.pack(anchor="w", padx=20, pady=(15, 10))

        # Camera Index
        cam_frame = ctk.CTkFrame(sec1, fg_color="transparent")
        cam_frame.pack(fill="x", padx=20, pady=5)

        cam_lbl = ctk.CTkLabel(cam_frame, text="Active Camera Source Index:", font=(config.FONT_FAMILY, 12, "bold"), text_color=config.COLOR_TEXT_MUTED)
        cam_lbl.pack(side="left")

        self.cam_opt = ctk.CTkOptionMenu(
            cam_frame,
            values=["0", "1", "2", "3"],
            fg_color="#0F172A",
            button_color=config.COLOR_PRIMARY
        )
        self.cam_opt.pack(side="right")

        # Confidence Slider
        conf_frame = ctk.CTkFrame(sec1, fg_color="transparent")
        conf_frame.pack(fill="x", padx=20, pady=10)

        self.conf_lbl = ctk.CTkLabel(conf_frame, text="Recognition Match Confidence: 60%", font=(config.FONT_FAMILY, 12, "bold"), text_color=config.COLOR_TEXT_MUTED)
        self.conf_lbl.pack(anchor="w")

        self.conf_slider = ctk.CTkSlider(
            conf_frame,
            from_=0.40,
            to=0.90,
            number_of_steps=50,
            command=self._on_slider_change
        )
        self.conf_slider.pack(fill="x", pady=5)

        # Voice Announcement Toggle
        voice_frame = ctk.CTkFrame(sec1, fg_color="transparent")
        voice_frame.pack(fill="x", padx=20, pady=10)

        self.voice_chk = ctk.CTkCheckBox(
            voice_frame,
            text="Enable Voice Announcements (Text-to-Speech)",
            font=(config.FONT_FAMILY, 12, "bold"),
            text_color=config.COLOR_TEXT_PRIMARY
        )
        self.voice_chk.pack(anchor="w")

        # --- SECTION 2: ATTENDANCE TIME WINDOW RULES ---
        sec2 = ctk.CTkFrame(scroll_container, fg_color=config.COLOR_CARD, corner_radius=12)
        sec2.pack(fill="x", pady=(0, 15))

        s2_title = ctk.CTkLabel(sec2, text="⏰ SHIFT ATTENDANCE TIME WINDOWS (24-Hour Format)", font=(config.FONT_FAMILY, 14, "bold"), text_color=config.COLOR_TEXT_PRIMARY)
        s2_title.pack(anchor="w", padx=20, pady=(15, 10))

        tw_frame = ctk.CTkFrame(sec2, fg_color="transparent")
        tw_frame.pack(fill="x", padx=20, pady=(0, 15))

        # Start Time
        ctk.CTkLabel(tw_frame, text="Shift Start Time:", font=(config.FONT_FAMILY, 11, "bold"), text_color=config.COLOR_TEXT_MUTED).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.start_time_entry = ctk.CTkEntry(tw_frame, width=100, fg_color="#0F172A")
        self.start_time_entry.grid(row=0, column=1, padx=5, pady=5)

        # Late Threshold Time
        ctk.CTkLabel(tw_frame, text="Late Threshold Time:", font=(config.FONT_FAMILY, 11, "bold"), text_color=config.COLOR_TEXT_MUTED).grid(row=0, column=2, padx=15, pady=5, sticky="w")
        self.late_time_entry = ctk.CTkEntry(tw_frame, width=100, fg_color="#0F172A")
        self.late_time_entry.grid(row=0, column=3, padx=5, pady=5)

        # End Time
        ctk.CTkLabel(tw_frame, text="Shift End Time:", font=(config.FONT_FAMILY, 11, "bold"), text_color=config.COLOR_TEXT_MUTED).grid(row=0, column=4, padx=15, pady=5, sticky="w")
        self.end_time_entry = ctk.CTkEntry(tw_frame, width=100, fg_color="#0F172A")
        self.end_time_entry.grid(row=0, column=5, padx=5, pady=5)

        # Save Settings Button
        save_btn = ctk.CTkButton(
            sec2,
            text="💾 SAVE CONFIGURATION SETTINGS",
            font=(config.FONT_FAMILY, 12, "bold"),
            fg_color=config.COLOR_PRIMARY,
            height=38,
            command=self.save_settings
        )
        save_btn.pack(fill="x", padx=20, pady=(0, 15))

        # --- SECTION 3: DATABASE BACKUP & RESTORE ---
        sec3 = ctk.CTkFrame(scroll_container, fg_color=config.COLOR_CARD, corner_radius=12)
        sec3.pack(fill="x", pady=0)

        s3_title = ctk.CTkLabel(sec3, text="💾 DATABASE BACKUP & RECOVERY", font=(config.FONT_FAMILY, 14, "bold"), text_color=config.COLOR_TEXT_PRIMARY)
        s3_title.pack(anchor="w", padx=20, pady=(15, 10))

        b_btn_frame = ctk.CTkFrame(sec3, fg_color="transparent")
        b_btn_frame.pack(fill="x", padx=20, pady=(0, 10))

        manual_b_btn = ctk.CTkButton(
            b_btn_frame,
            text="📦 Create Instant Database Backup",
            fg_color=config.COLOR_SUCCESS,
            command=self._create_backup
        )
        manual_b_btn.pack(side="left")

        # Scrollable Backups List
        self.backup_scroll = ctk.CTkScrollableFrame(sec3, fg_color="#0F172A", height=150)
        self.backup_scroll.pack(fill="x", padx=20, pady=(0, 15))

    def _on_slider_change(self, val: float):
        pct = int(val * 100)
        self.conf_lbl.configure(text=f"Recognition Match Confidence: {pct}%")

    def load_settings(self):
        cam_idx = self.db.get_setting("camera_index", str(config.DEFAULT_CAMERA_INDEX))
        conf_val = float(self.db.get_setting("confidence_threshold", str(config.DEFAULT_CONFIDENCE_THRESHOLD)))
        voice_on = self.db.get_setting("voice_enabled", "1") == "1"

        start_t = self.db.get_setting("attendance_start", config.DEFAULT_ATTENDANCE_START)
        late_t = self.db.get_setting("late_threshold", config.DEFAULT_LATE_THRESHOLD)
        end_t = self.db.get_setting("attendance_end", config.DEFAULT_ATTENDANCE_END)

        self.cam_opt.set(cam_idx)
        self.conf_slider.set(conf_val)
        self._on_slider_change(conf_val)

        if voice_on:
            self.voice_chk.select()
        else:
            self.voice_chk.deselect()

        self.start_time_entry.delete(0, "end")
        self.start_time_entry.insert(0, start_t)

        self.late_time_entry.delete(0, "end")
        self.late_time_entry.insert(0, late_t)

        self.end_time_entry.delete(0, "end")
        self.end_time_entry.insert(0, end_t)

    def save_settings(self):
        self.db.set_setting("camera_index", self.cam_opt.get())
        self.db.set_setting("confidence_threshold", f"{self.conf_slider.get():.2f}")
        self.db.set_setting("voice_enabled", "1" if self.voice_chk.get() == 1 else "0")

        self.db.set_setting("attendance_start", self.start_time_entry.get().strip())
        self.db.set_setting("late_threshold", self.late_time_entry.get().strip())
        self.db.set_setting("attendance_end", self.end_time_entry.get().strip())

        self.show_toast("Settings Saved", "System configuration settings updated successfully.")

    def _create_backup(self):
        b_path = self.backup_mgr.create_backup(tag="user")
        if b_path:
            self.show_toast("Backup Created", "Database backup saved successfully.")
            self.load_backups_list()
        else:
            self.show_toast("Error", "Failed to create database backup.")

    def load_backups_list(self):
        for w in self.backup_scroll.winfo_children():
            w.destroy()

        backups = self.backup_mgr.list_backups()
        if not backups:
            lbl = ctk.CTkLabel(self.backup_scroll, text="No database backups found.", font=(config.FONT_FAMILY, 11, "italic"), text_color=config.COLOR_TEXT_MUTED)
            lbl.pack(pady=10)
            return

        for b in backups:
            row = ctk.CTkFrame(self.backup_scroll, fg_color="#1E293B", height=32)
            row.pack(fill="x", pady=2)

            info = f"📄 {b['filename']} ({b['size_kb']} KB) - {b['modified']}"
            lbl = ctk.CTkLabel(row, text=info, font=(config.FONT_FAMILY, 11), text_color=config.COLOR_TEXT_PRIMARY)
            lbl.pack(side="left", padx=10)

            rst_btn = ctk.CTkButton(
                row,
                text="Restore",
                width=60,
                height=24,
                fg_color=config.COLOR_WARNING,
                command=lambda path=b['path']: self._restore_backup(path)
            )
            rst_btn.pack(side="right", padx=10)

    def _restore_backup(self, path: str):
        if self.backup_mgr.restore_backup(path):
            self.show_toast("Database Restored", f"Successfully restored database from file.")
        else:
            self.show_toast("Restore Error", "Failed to restore database backup.")
