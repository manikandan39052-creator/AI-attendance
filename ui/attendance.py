"""
FaceAttend AI Pro - Real-Time Facial Attendance Feed View
Displays real-time video stream overlay, recognition HUD, duplicate prevention alerts, and live log list.
"""

import customtkinter as ctk
import cv2
from datetime import datetime
from typing import Callable, Optional
import config
from core.database import DatabaseManager
from core.camera import CameraStream
from core.recognizer import RealtimeRecognizer
from core.attendance_manager import AttendanceManager
from core.excel_manager import ExcelManager
from core.voice import VoiceEngine
from core.utils import cv2_to_pillow
from core.logger import log_info

class AttendanceView(ctk.CTkFrame):
    def __init__(self, parent, db: DatabaseManager, show_toast: Callable[[str, str], None]):
        super().__init__(parent, fg_color=config.COLOR_BG)
        self.db = db
        self.show_toast = show_toast

        self.camera_stream: Optional[CameraStream] = None
        self.recognizer = RealtimeRecognizer()
        self.attendance_mgr = AttendanceManager(db)
        self.excel_mgr = ExcelManager(db)

        self.voice = VoiceEngine().start()
        self.is_running = False
        self.last_voice_times = {}  # Prevent voice spam

        self._create_widgets()

    def _create_widgets(self):
        # Header
        header = ctk.CTkFrame(self, fg_color=config.COLOR_CARD, corner_radius=12)
        header.pack(fill="x", padx=15, pady=(15, 10))

        title = ctk.CTkLabel(
            header,
            text="🎥 REAL-TIME AI FACIAL ATTENDANCE MONITOR",
            font=(config.FONT_FAMILY, 16, "bold"),
            text_color=config.COLOR_TEXT_PRIMARY
        )
        title.pack(side="left", padx=20, pady=15)

        # Main Split Content
        main_split = ctk.CTkFrame(self, fg_color="transparent")
        main_split.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Left Column: Video Feed HUD
        left_card = ctk.CTkFrame(main_split, fg_color=config.COLOR_CARD, corner_radius=12)
        left_card.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Camera Display Canvas
        self.canvas_label = ctk.CTkLabel(
            left_card,
            text="Camera Stream Inactive\nClick 'START ATTENDANCE CAMERA' Below",
            fg_color="#0B1329",
            corner_radius=10,
            font=(config.FONT_FAMILY, 14, "bold"),
            text_color=config.COLOR_TEXT_MUTED
        )
        self.canvas_label.pack(fill="both", expand=True, padx=15, pady=15)

        # Control Buttons
        btn_frame = ctk.CTkFrame(left_card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.start_btn = ctk.CTkButton(
            btn_frame,
            text="▶️ START ATTENDANCE CAMERA",
            font=(config.FONT_FAMILY, 13, "bold"),
            fg_color=config.COLOR_SUCCESS,
            height=40,
            command=self.start_attendance
        )
        self.start_btn.pack(side="left", expand=True, fill="x", padx=4)

        self.stop_btn = ctk.CTkButton(
            btn_frame,
            text="⏹️ STOP CAMERA",
            font=(config.FONT_FAMILY, 13, "bold"),
            fg_color=config.COLOR_DANGER,
            height=40,
            command=self.stop_attendance,
            state="disabled"
        )
        self.stop_btn.pack(side="right", expand=True, fill="x", padx=4)

        # Right Column: Today's Live Attendance Feed
        right_card = ctk.CTkFrame(main_split, fg_color=config.COLOR_CARD, corner_radius=12, width=380)
        right_card.pack(side="right", fill="both", padx=(0, 0))

        r_title = ctk.CTkLabel(right_card, text="⚡ LIVE MARKED FEED", font=(config.FONT_FAMILY, 14, "bold"), text_color=config.COLOR_TEXT_PRIMARY)
        r_title.pack(anchor="w", padx=15, pady=(15, 10))

        self.feed_scroll = ctk.CTkScrollableFrame(right_card, fg_color="#0F172A", width=340)
        self.feed_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def start_attendance(self):
        if not self.is_running:
            # Reload recognizer model
            self.recognizer.load_model()
            cam_idx = int(self.db.get_setting("camera_index", str(config.DEFAULT_CAMERA_INDEX)))
            self.camera_stream = CameraStream(src=cam_idx).start()
            self.is_running = True

            self.start_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
            self._update_loop()

    def _update_loop(self):
        if self.is_running and self.camera_stream:
            grabbed, frame, fps = self.camera_stream.read()
            if grabbed:
                display_frame = frame.copy()
                conf_thresh = float(self.db.get_setting("confidence_threshold", str(config.DEFAULT_CONFIDENCE_THRESHOLD)))
                recognized = self.recognizer.recognize_faces(frame, confidence_thresh=conf_thresh)

                for item in recognized:
                    x, y, w, h = item['box']
                    s_id = item['student_id']
                    conf = item['confidence']
                    is_live = item['is_live']

                    if s_id != "Unknown" and is_live:
                        # Attempt to mark attendance
                        success, msg, s_info = self.attendance_mgr.process_student_recognition(s_id, conf)

                        color = (16, 185, 129)  # Emerald green
                        label_text = f"{s_info.get('name', s_id)} ({int(conf * 100)}%)"

                        if success:
                            # Add card to feed
                            self._add_feed_card(s_info, datetime.now().strftime("%H:%M:%S"))
                            # Sync monthly Excel sheet
                            self.excel_mgr.generate_monthly_sheet()

                            # Voice notification
                            voice_msg = f"Welcome {s_info.get('name', '')}, attendance marked."
                            now_ts = datetime.now().timestamp()
                            if s_id not in self.last_voice_times or (now_ts - self.last_voice_times[s_id]) > 10.0:
                                self.voice.speak(voice_msg)
                                self.last_voice_times[s_id] = now_ts
                    else:
                        color = (239, 68, 68) if not is_live else (245, 158, 11)
                        label_text = f"Unknown / Spoof ({int(conf * 100)}%)"

                        # Record unknown face if enabled
                        if s_id == "Unknown" and not is_live:
                            unk_path = self.recognizer.save_unknown_face(frame, (x, y, w, h))
                            if unk_path:
                                self.db.record_unknown_face(unk_path, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

                    # Draw Bounding Box & HUD
                    cv2.rectangle(display_frame, (x, y), (x+w, y+h), color, 2)
                    cv2.rectangle(display_frame, (x, y-30), (x+w, y), color, -1)
                    cv2.putText(display_frame, label_text, (x+5, y-8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

                # Overlay Live Stats
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cv2.putText(display_frame, f"FPS: {int(fps)} | {now_str}", (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (6, 182, 212), 2)

                # Render Frame to CustomTkinter Label
                pil_img = cv2_to_pillow(display_frame, size=(640, 440))
                ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(640, 440))
                self.canvas_label.configure(image=ctk_img, text="")

            self.after(30, self._update_loop)

    def _add_feed_card(self, s_info: dict, time_str: str):
        card = ctk.CTkFrame(self.feed_scroll, fg_color="#1E293B", corner_radius=8, border_width=1, border_color=config.COLOR_SUCCESS)
        card.pack(fill="x", pady=4)

        t_lbl = ctk.CTkLabel(card, text=f"✅ {time_str}", font=(config.FONT_FAMILY, 10, "bold"), text_color=config.COLOR_SUCCESS)
        t_lbl.pack(anchor="w", padx=10, pady=(6, 0))

        n_lbl = ctk.CTkLabel(card, text=s_info.get("name", "Student"), font=(config.FONT_FAMILY, 12, "bold"), text_color=config.COLOR_TEXT_PRIMARY)
        n_lbl.pack(anchor="w", padx=10, pady=2)

        sub_lbl = ctk.CTkLabel(card, text=f"Roll: {s_info.get('roll_no', '')} | Dept: {s_info.get('department', '')}", font=(config.FONT_FAMILY, 10), text_color=config.COLOR_TEXT_MUTED)
        sub_lbl.pack(anchor="w", padx=10, pady=(0, 6))

    def stop_attendance(self):
        self.is_running = False
        if self.camera_stream:
            self.camera_stream.stop()
            self.camera_stream = None
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.canvas_label.configure(image="", text="Camera Feed Stopped")
