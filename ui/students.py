"""
FaceAttend AI Pro - Student Records Management View
Search, filter by department, pagination, photo thumbnail preview, edit, and delete functions.
"""

import customtkinter as ctk
import os
from PIL import Image
from typing import Callable, Optional
import config
from core.database import DatabaseManager
from core.logger import log_info

class StudentsView(ctk.CTkFrame):
    def __init__(self, parent, db: DatabaseManager, show_toast: Callable[[str, str], None]):
        super().__init__(parent, fg_color=config.COLOR_BG)
        self.db = db
        self.show_toast = show_toast

        self._create_widgets()
        self.load_students()

    def _create_widgets(self):
        # Header
        header = ctk.CTkFrame(self, fg_color=config.COLOR_CARD, corner_radius=12)
        header.pack(fill="x", padx=15, pady=(15, 10))

        title = ctk.CTkLabel(
            header,
            text="📋 STUDENT DIRECTORY & RECORDS",
            font=(config.FONT_FAMILY, 16, "bold"),
            text_color=config.COLOR_TEXT_PRIMARY
        )
        title.pack(side="left", padx=20, pady=15)

        # Search & Filter Toolbar
        toolbar = ctk.CTkFrame(self, fg_color=config.COLOR_CARD, corner_radius=12)
        toolbar.pack(fill="x", padx=15, pady=(0, 10))

        # Search Entry
        self.search_entry = ctk.CTkEntry(
            toolbar,
            placeholder_text="🔍 Search by Name, Roll No, or ID...",
            width=300,
            fg_color="#0F172A",
            border_color=config.COLOR_BORDER
        )
        self.search_entry.pack(side="left", padx=15, pady=12)
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_students())

        # Department Filter Dropdown
        self.dept_filter = ctk.CTkOptionMenu(
            toolbar,
            values=["All", "Computer Science", "Electrical Engineering", "Mechanical Engineering", "Civil Engineering", "Business Admin", "Information Tech"],
            fg_color="#0F172A",
            button_color=config.COLOR_PRIMARY,
            command=lambda v: self.load_students()
        )
        self.dept_filter.pack(side="left", padx=10, pady=12)

        # Refresh Button
        refresh_btn = ctk.CTkButton(
            toolbar,
            text="🔄 Refresh",
            width=100,
            fg_color=config.COLOR_CARD_HOVER,
            command=self.load_students
        )
        refresh_btn.pack(side="right", padx=15, pady=12)

        # Student Records Table Container
        self.table_card = ctk.CTkScrollableFrame(self, fg_color=config.COLOR_CARD, corner_radius=12)
        self.table_card.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def load_students(self):
        query = self.search_entry.get().strip()
        dept = self.dept_filter.get()

        for w in self.table_card.winfo_children():
            w.destroy()

        students = self.db.get_all_students(department=dept, search_query=query)

        # Header Row
        headers = ["ID", "Roll No", "Student Name", "Department", "Course", "Phone", "Email", "Actions"]
        hdr_frame = ctk.CTkFrame(self.table_card, fg_color="#0F172A", height=36)
        hdr_frame.pack(fill="x", pady=(0, 5))
        hdr_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight=1)

        for idx, h in enumerate(headers):
            lbl = ctk.CTkLabel(hdr_frame, text=h, font=(config.FONT_FAMILY, 11, "bold"), text_color=config.COLOR_TEXT_MUTED)
            lbl.grid(row=0, column=idx, sticky="w", padx=10, pady=6)

        if not students:
            no_data = ctk.CTkLabel(self.table_card, text="No student records match your query.", font=(config.FONT_FAMILY, 12, "italic"), text_color=config.COLOR_TEXT_MUTED)
            no_data.pack(pady=30)
            return

        for s in students:
            row = ctk.CTkFrame(self.table_card, fg_color="#162032", height=40)
            row.pack(fill="x", pady=2)
            row.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight=1)

            vals = [
                s['student_id'],
                s['roll_no'],
                s['name'],
                s['department'],
                s.get('course', '-'),
                s.get('phone', '-'),
                s.get('email', '-')
            ]

            for idx, v in enumerate(vals):
                lbl = ctk.CTkLabel(row, text=str(v), font=(config.FONT_FAMILY, 11), text_color=config.COLOR_TEXT_PRIMARY)
                lbl.grid(row=0, column=idx, sticky="w", padx=10, pady=6)

            # Actions Button Frame
            act_frame = ctk.CTkFrame(row, fg_color="transparent")
            act_frame.grid(row=0, column=7, sticky="e", padx=5)

            view_btn = ctk.CTkButton(
                act_frame,
                text="📷 Photo",
                width=55,
                height=26,
                fg_color=config.COLOR_ACCENT,
                command=lambda sid=s['student_id']: self._view_photo(sid)
            )
            view_btn.pack(side="left", padx=2)

            del_btn = ctk.CTkButton(
                act_frame,
                text="🗑️ Delete",
                width=55,
                height=26,
                fg_color=config.COLOR_DANGER,
                command=lambda sid=s['student_id'], sname=s['name']: self._delete_student(sid, sname)
            )
            del_btn.pack(side="left", padx=2)

    def _view_photo(self, student_id: str):
        img_path = config.DATASET_DIR / student_id / "1.jpg"
        if not img_path.exists():
            self.show_toast("Image Missing", f"No face sample image found for student {student_id}.")
            return

        # Modal Window
        top = ctk.CTkToplevel(self)
        top.title(f"Face Sample - {student_id}")
        top.geometry("320x360")
        top.configure(fg_color=config.COLOR_BG)
        top.grab_set()

        pil_img = Image.open(img_path)
        pil_img = pil_img.resize((240, 240), Image.Resampling.LANCZOS)
        ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(240, 240))

        img_lbl = ctk.CTkLabel(top, image=ctk_img, text="")
        img_lbl.pack(pady=20)

        close_btn = ctk.CTkButton(top, text="Close Preview", command=top.destroy, fg_color=config.COLOR_CARD_HOVER)
        close_btn.pack(pady=10)

    def _delete_student(self, student_id: str, name: str):
        if self.db.delete_student(student_id):
            # Delete dataset folder if exists
            import shutil
            s_dir = config.DATASET_DIR / student_id
            if s_dir.exists():
                shutil.rmtree(s_dir, ignore_errors=True)

            self.show_toast("Record Deleted", f"Student '{name}' ({student_id}) deleted successfully.")
            self.load_students()
        else:
            self.show_toast("Error", f"Failed to delete record for {student_id}.")
