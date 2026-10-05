"""
FaceAttend AI Pro - Student Registration & Face Capture View
Handles student detail entry with full validation and auto 100-sample facial dataset capture.
"""

import customtkinter as ctk
import cv2
from PIL import Image
from datetime import datetime
from typing import Callable, Optional
import config
from core.database import DatabaseManager
from core.camera import CameraStream
from core.capture import FaceCaptureManager
from core.utils import validate_email, validate_phone, cv2_to_pillow
from core.logger import log_info, log_error

class RegisterView(ctk.CTkFrame):
    def __init__(self, parent, db: DatabaseManager, show_toast: Callable[[str, str], None]):
        super().__init__(parent, fg_color=config.COLOR_BG)
        self.db = db
        self.show_toast = show_toast

        self.camera_stream: Optional[CameraStream] = None
        self.capture_mgr = FaceCaptureManager()
        self.is_capturing = False
        self.sample_count = 0

        self.entries = {}
        self._create_widgets()

    def _create_widgets(self):
        # Header Banner
        header = ctk.CTkFrame(self, fg_color=config.COLOR_CARD, corner_radius=12)
        header.pack(fill="x", padx=15, pady=(15, 10))

        title = ctk.CTkLabel(
            header,
            text="👤 STUDENT REGISTRATION & FACIAL ENROLLMENT",
            font=(config.FONT_FAMILY, 16, "bold"),
            text_color=config.COLOR_TEXT_PRIMARY
        )
        title.pack(side="left", padx=20, pady=15)

        # Main 2-Column Split Frame
        split_frame = ctk.CTkFrame(self, fg_color="transparent")
        split_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Left Column: Form Fields
        form_card = ctk.CTkScrollableFrame(split_frame, fg_color=config.COLOR_CARD, corner_radius=12)
        form_card.pack(side="left", fill="both", expand=True, padx=(0, 10))

        fields_def = [
            ("student_id", "Student ID *", "e.g. STU1001"),
            ("roll_no", "Roll Number *", "e.g. 2027-CS-01"),
            ("name", "Full Name *", "e.g. Alexander Pierce"),
            ("department", "Department *", "e.g. Computer Science"),
            ("course", "Course / Degree", "e.g. B.Tech"),
            ("year", "Academic Year", "e.g. 3rd Year"),
            ("semester", "Semester", "e.g. 6th Semester"),
            ("section", "Section", "e.g. Section-A"),
            ("gender", "Gender", "Male / Female / Other"),
            ("phone", "Phone Number", "e.g. +1 555-0192"),
            ("email", "Email Address", "e.g. alex@university.edu"),
            ("address", "Residential Address", "e.g. 104 Campus Way"),
            ("parent_name", "Parent / Guardian Name", "e.g. Robert Pierce"),
            ("parent_phone", "Parent Phone", "e.g. +1 555-0199"),
            ("blood_group", "Blood Group", "e.g. O+"),
            ("dob", "Date of Birth (YYYY-MM-DD)", "e.g. 2004-05-14"),
            ("admission_no", "Admission Number", "e.g. ADM-2024-99")
        ]

        for key, label_text, placeholder in fields_def:
            lbl = ctk.CTkLabel(form_card, text=label_text, font=(config.FONT_FAMILY, 11, "bold"), text_color=config.COLOR_TEXT_MUTED)
            lbl.pack(anchor="w", padx=15, pady=(8, 2))

            if key == "department":
                entry = ctk.CTkOptionMenu(
                    form_card,
                    values=["Computer Science", "Electrical Engineering", "Mechanical Engineering", "Civil Engineering", "Business Admin", "Information Tech"],
                    fg_color="#0F172A",
                    button_color=config.COLOR_PRIMARY,
                    text_color=config.COLOR_TEXT_PRIMARY,
                    height=36
                )
            elif key == "gender":
                entry = ctk.CTkOptionMenu(
                    form_card,
                    values=["Male", "Female", "Other"],
                    fg_color="#0F172A",
                    button_color=config.COLOR_PRIMARY,
                    text_color=config.COLOR_TEXT_PRIMARY,
                    height=36
                )
            else:
                entry = ctk.CTkEntry(
                    form_card,
                    placeholder_text=placeholder,
                    fg_color="#0F172A",
                    border_color=config.COLOR_BORDER,
                    height=36
                )

            entry.pack(fill="x", padx=15, pady=(0, 4))
            self.entries[key] = entry

        # Auto-fill sample Student ID
        auto_id = f"STU{int(datetime.now().timestamp()) % 10000:04d}"
        self.entries['student_id'].insert(0, auto_id)

        # Right Column: Camera Capture & Dataset Status
        right_card = ctk.CTkFrame(split_frame, fg_color=config.COLOR_CARD, corner_radius=12)
        right_card.pack(side="right", fill="both", expand=True)

        cam_title = ctk.CTkLabel(right_card, text="📸 FACE DATASET ENROLLMENT", font=(config.FONT_FAMILY, 14, "bold"), text_color=config.COLOR_TEXT_PRIMARY)
        cam_title.pack(anchor="w", padx=15, pady=(15, 10))

        # Video Canvas Preview
        self.video_canvas = ctk.CTkLabel(right_card, text="Camera Preview Standby\nClick 'Start Capture' Below", fg_color="#0B1329", corner_radius=8, height=280)
        self.video_canvas.pack(fill="x", padx=15, pady=5)

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(right_card, progress_color=config.COLOR_SUCCESS, fg_color="#0F172A")
        self.progress_bar.pack(fill="x", padx=15, pady=10)
        self.progress_bar.set(0.0)

        self.status_lbl = ctk.CTkLabel(right_card, text="Status: Ready to capture 100 face images", font=(config.FONT_FAMILY, 12, "bold"), text_color=config.COLOR_ACCENT)
        self.status_lbl.pack(pady=5)

        # Action Buttons
        btn_frame = ctk.CTkFrame(right_card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=15)

        self.start_cam_btn = ctk.CTkButton(
            btn_frame,
            text="📷 Start Face Capture",
            font=(config.FONT_FAMILY, 12, "bold"),
            fg_color=config.COLOR_ACCENT,
            command=self._start_capture
        )
        self.start_cam_btn.pack(side="left", expand=True, fill="x", padx=4)

        self.stop_cam_btn = ctk.CTkButton(
            btn_frame,
            text="⏹️ Stop Camera",
            font=(config.FONT_FAMILY, 12, "bold"),
            fg_color=config.COLOR_DANGER,
            command=self._stop_capture,
            state="disabled"
        )
        self.stop_cam_btn.pack(side="right", expand=True, fill="x", padx=4)

        # Save Record Button
        self.save_btn = ctk.CTkButton(
            right_card,
            text="💾 SAVE STUDENT & COMPLETE ENROLLMENT",
            font=(config.FONT_FAMILY, 13, "bold"),
            fg_color=config.COLOR_SUCCESS,
            height=42,
            command=self._save_student
        )
        self.save_btn.pack(fill="x", padx=15, pady=(5, 15))

    def _start_capture(self):
        s_id = self.entries['student_id'].get().strip()
        if not s_id:
            self.show_toast("Validation Error", "Please enter Student ID before capturing face images.")
            return

        if not self.is_capturing:
            cam_idx = int(self.db.get_setting("camera_index", str(config.DEFAULT_CAMERA_INDEX)))
            self.camera_stream = CameraStream(src=cam_idx).start()
            self.is_capturing = True
            self.sample_count = 0
            self.start_cam_btn.configure(state="disabled")
            self.stop_cam_btn.configure(state="normal")
            self._update_video_feed()

    def _update_video_feed(self):
        if self.is_capturing and self.camera_stream:
            grabbed, frame, fps = self.camera_stream.read()
            if grabbed:
                s_id = self.entries['student_id'].get().strip()
                success, status_msg, proc_frame, self.sample_count = self.capture_mgr.process_and_save_face(
                    frame=frame,
                    student_id=s_id,
                    sample_count=self.sample_count,
                    target_total=config.DEFAULT_DATASET_SAMPLE_COUNT
                )

                # Update progress bar
                pct = self.sample_count / config.DEFAULT_DATASET_SAMPLE_COUNT
                self.progress_bar.set(pct)
                self.status_lbl.configure(text=f"Status: {status_msg}")

                # Display frame
                pil_img = cv2_to_pillow(proc_frame, size=(380, 260))
                ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(380, 260))
                self.video_canvas.configure(image=ctk_img, text="")

                if self.sample_count >= config.DEFAULT_DATASET_SAMPLE_COUNT:
                    self._stop_capture()
                    self.show_toast("Capture Complete", f"Successfully captured 100 face images for {s_id}!")
                    return

            self.after(30, self._update_video_feed)

    def _stop_capture(self):
        self.is_capturing = False
        if self.camera_stream:
            self.camera_stream.stop()
            self.camera_stream = None
        self.start_cam_btn.configure(state="normal")
        self.stop_cam_btn.configure(state="disabled")
        self.video_canvas.configure(image="", text="Camera Feed Stopped")

    def _save_student(self):
        # Validate Fields
        s_id = self.entries['student_id'].get().strip()
        roll_no = self.entries['roll_no'].get().strip()
        name = self.entries['name'].get().strip()
        dept = self.entries['department'].get()
        email = self.entries['email'].get().strip()
        phone = self.entries['phone'].get().strip()

        if not s_id or not roll_no or not name:
            self.show_toast("Error", "Student ID, Roll Number, and Full Name are mandatory fields.")
            return

        if self.db.is_student_id_exists(s_id):
            self.show_toast("Duplicate Error", f"Student ID '{s_id}' already exists in database.")
            return

        if self.db.is_roll_no_exists(roll_no):
            self.show_toast("Duplicate Error", f"Roll Number '{roll_no}' is already registered.")
            return

        if email and not validate_email(email):
            self.show_toast("Validation Error", "Please enter a valid email address.")
            return

        if phone and not validate_phone(phone):
            self.show_toast("Validation Error", "Please enter a valid phone number.")
            return

        # Prepare dict
        data = {key: self.entries[key].get().strip() if hasattr(self.entries[key], 'get') else self.entries[key].get() for key in self.entries}
        data['photo_path'] = str(config.DATASET_DIR / s_id / "1.jpg")

        if self.db.add_student(data):
            self.show_toast("Success", f"Student '{name}' registered successfully!")
            log_info(f"New student added: {s_id} - {name}")
            # Reset fields
            for k, e in self.entries.items():
                if hasattr(e, 'delete'):
                    e.delete(0, 'end')
            auto_id = f"STU{int(datetime.now().timestamp()) % 10000:04d}"
            self.entries['student_id'].insert(0, auto_id)
            self.progress_bar.set(0.0)
        else:
            self.show_toast("Database Error", "Failed to save student record to database.")
