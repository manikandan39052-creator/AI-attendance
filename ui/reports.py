"""
FaceAttend AI Pro - Visual Analytics & Reports View
Displays interactive Matplotlib charts and exports PDF/CSV/Excel reports.
"""

import customtkinter as ctk
import os
from PIL import Image
from datetime import datetime
from typing import Callable
import config
from core.database import DatabaseManager
from core.report_generator import ReportGenerator
from core.excel_manager import ExcelManager

class ReportsView(ctk.CTkFrame):
    def __init__(self, parent, db: DatabaseManager, show_toast: Callable[[str, str], None]):
        super().__init__(parent, fg_color=config.COLOR_BG)
        self.db = db
        self.show_toast = show_toast

        self.report_gen = ReportGenerator(db)
        self.excel_mgr = ExcelManager(db)

        self._create_widgets()
        self.generate_and_render_charts()

    def _create_widgets(self):
        # Header
        header = ctk.CTkFrame(self, fg_color=config.COLOR_CARD, corner_radius=12)
        header.pack(fill="x", padx=15, pady=(15, 10))

        title = ctk.CTkLabel(
            header,
            text="📊 ATTENDANCE ANALYTICS & EXPORT CENTER",
            font=(config.FONT_FAMILY, 16, "bold"),
            text_color=config.COLOR_TEXT_PRIMARY
        )
        title.pack(side="left", padx=20, pady=15)

        # Toolbar Frame
        toolbar = ctk.CTkFrame(self, fg_color=config.COLOR_CARD, corner_radius=12)
        toolbar.pack(fill="x", padx=15, pady=(0, 10))

        # Date Entry
        date_lbl = ctk.CTkLabel(toolbar, text="Target Date:", font=(config.FONT_FAMILY, 11, "bold"), text_color=config.COLOR_TEXT_MUTED)
        date_lbl.pack(side="left", padx=(15, 5), pady=12)

        self.date_entry = ctk.CTkEntry(
            toolbar,
            width=120,
            fg_color="#0F172A",
            border_color=config.COLOR_BORDER
        )
        self.date_entry.pack(side="left", padx=5, pady=12)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Dept Filter
        self.dept_menu = ctk.CTkOptionMenu(
            toolbar,
            values=["All", "Computer Science", "Electrical Engineering", "Mechanical Engineering", "Civil Engineering", "Business Admin"],
            fg_color="#0F172A",
            button_color=config.COLOR_PRIMARY
        )
        self.dept_menu.pack(side="left", padx=10, pady=12)

        # Render Charts Button
        gen_btn = ctk.CTkButton(
            toolbar,
            text="📈 Update Analytics",
            fg_color=config.COLOR_ACCENT,
            command=self.generate_and_render_charts
        )
        gen_btn.pack(side="left", padx=10, pady=12)

        # Export Action Buttons
        pdf_btn = ctk.CTkButton(
            toolbar,
            text="📄 Export PDF",
            fg_color=config.COLOR_DANGER,
            command=self._export_pdf
        )
        pdf_btn.pack(side="right", padx=10, pady=12)

        csv_btn = ctk.CTkButton(
            toolbar,
            text="📊 Export CSV",
            fg_color=config.COLOR_SUCCESS,
            command=self._export_csv
        )
        csv_btn.pack(side="right", padx=5, pady=12)

        excel_btn = ctk.CTkButton(
            toolbar,
            text="📗 Sync Excel",
            fg_color=config.COLOR_PRIMARY,
            command=self._sync_excel
        )
        excel_btn.pack(side="right", padx=5, pady=12)

        # Charts Display Split Container
        charts_split = ctk.CTkScrollableFrame(self, fg_color="transparent")
        charts_split.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Chart 1: Bar Chart Card
        self.bar_card = ctk.CTkFrame(charts_split, fg_color=config.COLOR_CARD, corner_radius=12)
        self.bar_card.pack(fill="x", pady=(0, 15))

        self.bar_lbl = ctk.CTkLabel(self.bar_card, text="Generating Department Bar Chart...", font=(config.FONT_FAMILY, 12), text_color=config.COLOR_TEXT_MUTED)
        self.bar_lbl.pack(pady=40)

        # Chart 2: Pie Chart Card
        self.pie_card = ctk.CTkFrame(charts_split, fg_color=config.COLOR_CARD, corner_radius=12)
        self.pie_card.pack(fill="x", pady=0)

        self.pie_lbl = ctk.CTkLabel(self.pie_card, text="Generating Attendance Pie Chart...", font=(config.FONT_FAMILY, 12), text_color=config.COLOR_TEXT_MUTED)
        self.pie_lbl.pack(pady=40)

    def generate_and_render_charts(self):
        target_date = self.date_entry.get().strip() or datetime.now().strftime("%Y-%m-%d")

        # 1. Bar Chart
        bar_path = self.report_gen.generate_department_bar_chart(target_date)
        if os.path.exists(bar_path):
            pil_bar = Image.open(bar_path)
            ctk_bar = ctk.CTkImage(light_image=pil_bar, dark_image=pil_bar, size=(650, 350))
            self.bar_lbl.configure(image=ctk_bar, text="")
        else:
            self.bar_lbl.configure(text="Failed to generate Bar Chart.")

        # 2. Pie Chart
        pie_path = self.report_gen.generate_attendance_pie_chart(target_date)
        if os.path.exists(pie_path):
            pil_pie = Image.open(pie_path)
            ctk_pie = ctk.CTkImage(light_image=pil_pie, dark_image=pil_pie, size=(550, 350))
            self.pie_lbl.configure(image=ctk_pie, text="")
        else:
            self.pie_lbl.configure(text="Failed to generate Pie Chart.")

    def _export_pdf(self):
        target_date = self.date_entry.get().strip()
        dept = self.dept_menu.get()
        pdf_file = self.report_gen.export_pdf(date_str=target_date, department=dept)
        if pdf_file:
            self.show_toast("PDF Exported", f"Report saved to:\n{pdf_file}")
        else:
            self.show_toast("Export Error", "Failed to generate PDF report.")

    def _export_csv(self):
        target_date = self.date_entry.get().strip()
        dept = self.dept_menu.get()
        records = self.db.get_attendance_history(date_str=target_date, department=dept)
        if not records:
            self.show_toast("Notice", "No attendance records found for target date/department.")
            return

        csv_file = self.report_gen.export_csv(records, filename=f"Attendance_{target_date}.csv")
        if csv_file:
            self.show_toast("CSV Exported", f"File saved to:\n{csv_file}")
        else:
            self.show_toast("Export Error", "Failed to export CSV.")

    def _sync_excel(self):
        excel_path = self.excel_mgr.generate_monthly_sheet()
        self.show_toast("Excel Workbook Updated", f"Attendance workbook synced at:\n{excel_path}")
