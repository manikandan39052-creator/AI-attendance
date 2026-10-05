"""
FaceAttend AI Pro - Model Training View
Visual training interface displaying progress bars, ETA, and live console output log.
"""

import customtkinter as ctk
import threading
from typing import Callable
import config
from core.database import DatabaseManager
from core.training import ModelTrainer
from core.logger import log_info

class TrainView(ctk.CTkFrame):
    def __init__(self, parent, db: DatabaseManager, show_toast: Callable[[str, str], None]):
        super().__init__(parent, fg_color=config.COLOR_BG)
        self.db = db
        self.show_toast = show_toast
        self.trainer = ModelTrainer()

        self._create_widgets()

    def _create_widgets(self):
        # Header
        header = ctk.CTkFrame(self, fg_color=config.COLOR_CARD, corner_radius=12)
        header.pack(fill="x", padx=15, pady=(15, 10))

        title = ctk.CTkLabel(
            header,
            text="🧠 AI FACE MODEL TRAINER",
            font=(config.FONT_FAMILY, 16, "bold"),
            text_color=config.COLOR_TEXT_PRIMARY
        )
        title.pack(side="left", padx=20, pady=15)

        # Center Card
        card = ctk.CTkFrame(self, fg_color=config.COLOR_CARD, corner_radius=12)
        card.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        subtitle = ctk.CTkLabel(
            card,
            text="Extract face embeddings from student dataset images and build pickle neural weights file.",
            font=(config.FONT_FAMILY, 12, "normal"),
            text_color=config.COLOR_TEXT_MUTED
        )
        subtitle.pack(anchor="w", padx=20, pady=(20, 10))

        # Stats Cards Container
        stats_frame = ctk.CTkFrame(card, fg_color="transparent")
        stats_frame.pack(fill="x", padx=20, pady=10)

        self.lbl_faces = self._add_stat(stats_frame, 0, "FACES TRAINED", "0")
        self.lbl_eta = self._add_stat(stats_frame, 1, "ESTIMATED REMAINING", "--:--")
        self.lbl_model = self._add_stat(stats_frame, 2, "MODEL ENGINE", "Auto-Detect")

        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(card, progress_color=config.COLOR_ACCENT, fg_color="#0F172A", height=18)
        self.progress_bar.pack(fill="x", padx=20, pady=(20, 5))
        self.progress_bar.set(0.0)

        self.pct_label = ctk.CTkLabel(card, text="0.0%", font=(config.FONT_FAMILY, 12, "bold"), text_color=config.COLOR_TEXT_PRIMARY)
        self.pct_label.pack(pady=(0, 15))

        # Log Terminal Output Box
        log_title = ctk.CTkLabel(card, text="📄 TRAINING LOG OUTPUT", font=(config.FONT_FAMILY, 11, "bold"), text_color=config.COLOR_TEXT_MUTED)
        log_title.pack(anchor="w", padx=20, pady=(5, 2))

        self.log_textbox = ctk.CTkTextbox(
            card,
            fg_color="#0B1329",
            text_color="#10B981",
            font=("Consolas", 11),
            corner_radius=8
        )
        self.log_textbox.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        self.log_textbox.insert("1.0", "System ready for model training...\nClick 'Start AI Training' to begin.\n")

        # Start Training Button
        self.train_btn = ctk.CTkButton(
            card,
            text="🚀 START AI MODEL TRAINING",
            font=(config.FONT_FAMILY, 14, "bold"),
            fg_color=config.COLOR_PRIMARY,
            hover_color=config.COLOR_PRIMARY_HOVER,
            height=44,
            corner_radius=8,
            command=self._start_training_thread
        )
        self.train_btn.pack(fill="x", padx=20, pady=(0, 20))

    def _add_stat(self, parent, col: int, title: str, default_val: str):
        box = ctk.CTkFrame(parent, fg_color="#0F172A", corner_radius=8)
        box.pack(side="left", expand=True, fill="x", padx=5)

        t = ctk.CTkLabel(box, text=title, font=(config.FONT_FAMILY, 10, "bold"), text_color=config.COLOR_TEXT_MUTED)
        t.pack(padx=10, pady=(8, 2))

        v = ctk.CTkLabel(box, text=default_val, font=(config.FONT_FAMILY, 16, "bold"), text_color=config.COLOR_ACCENT)
        v.pack(padx=10, pady=(0, 8))
        return v

    def _start_training_thread(self):
        self.train_btn.configure(state="disabled")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.insert("end", "[INFO] Training process launched in background thread...\n")

        threading.Thread(target=self._run_training, daemon=True).start()

    def _run_training(self):
        def progress_cb(pct, status_text, faces_count, eta_sec):
            self.after(0, lambda: self._update_ui_progress(pct, status_text, faces_count, eta_sec))

        success, msg = self.trainer.train_model(progress_callback=progress_cb)

        self.after(0, lambda: self._on_training_finished(success, msg))

    def _update_ui_progress(self, pct: float, status_text: str, faces_count: int, eta_sec: float):
        self.progress_bar.set(pct / 100.0)
        self.pct_label.configure(text=f"{pct:.1f}%")
        self.lbl_faces.configure(text=str(faces_count))

        m, s = divmod(int(eta_sec), 60)
        self.lbl_eta.configure(text=f"{m:02d}:{s:02d}")

        self.log_textbox.insert("end", f"[PROGRESS] {status_text}\n")
        self.log_textbox.see("end")

    def _on_training_finished(self, success: bool, msg: str):
        self.train_btn.configure(state="normal")
        if success:
            self.show_toast("Success", "AI Face Model Training Completed Successfully!")
            self.log_textbox.insert("end", f"\n[SUCCESS] {msg}\n")
        else:
            self.show_toast("Error", f"Training Failed: {msg}")
            self.log_textbox.insert("end", f"\n[ERROR] {msg}\n")
        self.log_textbox.see("end")
