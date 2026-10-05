"""
FaceAttend AI Pro - Admin Dashboard View
Presents KPI metric cards, live clock, status indicators, quick actions, and today's attendance table.
"""

import customtkinter as ctk
from datetime import datetime
from typing import Callable
import config
from core.database import DatabaseManager

class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, db: DatabaseManager, navigate_callback: Callable[[str], None]):
        super().__init__(parent, fg_color=config.COLOR_BG)
        self.db = db
        self.navigate = navigate_callback

        self._create_widgets()
        self._update_clock()
        self.refresh_stats()

    def _create_widgets(self):
        # Container Grid
        self.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.grid_rowconfigure(2, weight=1)

        # --- HEADER & LIVE CLOCK BANNER ---
        header_frame = ctk.CTkFrame(self, fg_color=config.COLOR_CARD, corner_radius=12)
        header_frame.grid(row=0, column=0, columnspan=4, sticky="ew", padx=15, pady=(15, 10))

        title_lbl = ctk.CTkLabel(
            header_frame,
            text="📊 SYSTEM DASHBOARD & TELEMETRY",
            font=(config.FONT_FAMILY, 16, "bold"),
            text_color=config.COLOR_TEXT_PRIMARY
        )
        title_lbl.pack(side="left", padx=20, pady=15)

        # Clock Label
        self.clock_lbl = ctk.CTkLabel(
            header_frame,
            text="",
            font=(config.FONT_FAMILY, 13, "bold"),
            text_color=config.COLOR_ACCENT
        )
        self.clock_lbl.pack(side="right", padx=20)

        # --- KPI METRIC CARDS ---
        self.card_total = self._create_kpi_card(0, "TOTAL STUDENTS", "0", "👥", config.COLOR_PRIMARY)
        self.card_present = self._create_kpi_card(1, "PRESENT TODAY", "0", "✅", config.COLOR_SUCCESS)
        self.card_absent = self._create_kpi_card(2, "ABSENT TODAY", "0", "❌", config.COLOR_DANGER)
        self.card_pct = self._create_kpi_card(3, "ATTENDANCE RATE", "0.0%", "📈", config.COLOR_ACCENT)

        # --- QUICK ACTIONS MENU ---
        action_frame = ctk.CTkFrame(self, fg_color=config.COLOR_CARD, corner_radius=12)
        action_frame.grid(row=2, column=0, columnspan=4, sticky="ew", padx=15, pady=10)

        action_title = ctk.CTkLabel(
            action_frame,
            text="⚡ QUICK ACTIONS",
            font=(config.FONT_FAMILY, 14, "bold"),
            text_color=config.COLOR_TEXT_PRIMARY
        )
        action_title.pack(anchor="w", padx=20, pady=(12, 8))

        btn_container = ctk.CTkFrame(action_frame, fg_color="transparent")
        btn_container.pack(fill="x", padx=15, pady=(0, 15))

        actions = [
            ("📸 Register Student", "register", config.COLOR_PRIMARY),
            ("🧠 Train Model", "train", config.COLOR_ACCENT),
            ("🎥 Start Attendance", "attendance", config.COLOR_SUCCESS),
            ("📋 Student Records", "students", config.COLOR_PRIMARY),
            ("📊 Reports & Export", "reports", config.COLOR_WARNING),
            ("⚙️ Settings", "settings", "#64748B")
        ]

        for text, target_route, color in actions:
            b = ctk.CTkButton(
                btn_container,
                text=text,
                font=(config.FONT_FAMILY, 12, "bold"),
                fg_color=color,
                height=38,
                corner_radius=8,
                command=lambda r=target_route: self.navigate(r)
            )
            b.pack(side="left", expand=True, fill="x", padx=4)

        # --- TODAY'S LIVE ATTENDANCE LOG TABLE ---
        table_frame = ctk.CTkFrame(self, fg_color=config.COLOR_CARD, corner_radius=12)
        table_frame.grid(row=3, column=0, columnspan=4, sticky="nsew", padx=15, pady=(5, 15))

        table_title = ctk.CTkLabel(
            table_frame,
            text="🕒 TODAY'S ATTENDANCE ACTIVITY LOG",
            font=(config.FONT_FAMILY, 14, "bold"),
            text_color=config.COLOR_TEXT_PRIMARY
        )
        table_title.pack(anchor="w", padx=20, pady=(12, 8))

        # Scrollable table container
        self.scroll_table = ctk.CTkScrollableFrame(table_frame, fg_color="#0F172A", height=200)
        self.scroll_table.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def _create_kpi_card(self, col: int, title: str, default_val: str, icon: str, accent_color: str):
        card = ctk.CTkFrame(self, fg_color=config.COLOR_CARD, corner_radius=12, border_width=1, border_color=config.COLOR_BORDER)
        card.grid(row=1, column=col, sticky="ew", padx=15 if col==0 else (5, 15 if col==3 else 5), pady=10)

        header = ctk.CTkLabel(card, text=f"{icon}  {title}", font=(config.FONT_FAMILY, 11, "bold"), text_color=config.COLOR_TEXT_MUTED)
        header.pack(anchor="w", padx=15, pady=(12, 4))

        val_lbl = ctk.CTkLabel(card, text=default_val, font=(config.FONT_FAMILY, 24, "bold"), text_color=accent_color)
        val_lbl.pack(anchor="w", padx=15, pady=(0, 12))

        return val_lbl

    def _update_clock(self):
        now_str = datetime.now().strftime("📅 %A, %b %d, %Y  |  ⏰ %H:%M:%S")
        self.clock_lbl.configure(text=now_str)
        self.after(1000, self._update_clock)

    def refresh_stats(self):
        """Fetch and update live KPI numbers and table entries."""
        today_date = datetime.now().strftime("%Y-%m-%d")
        stats = self.db.get_dashboard_stats(today_date)

        self.card_total.configure(text=str(stats['total_students']))
        self.card_present.configure(text=str(stats['present_today']))
        self.card_absent.configure(text=str(stats['absent_today']))
        self.card_pct.configure(text=f"{stats['attendance_percentage']}%")

        # Clear and repopulate today's log table
        for widget in self.scroll_table.winfo_children():
            widget.destroy()

        # Header Row
        headers = ["Roll No", "Student Name", "Department", "Time", "Status", "Confidence"]
        hdr_frame = ctk.CTkFrame(self.scroll_table, fg_color="#1E293B", height=30)
        hdr_frame.pack(fill="x", pady=(0, 4))

        for idx, h in enumerate(headers):
            lbl = ctk.CTkLabel(hdr_frame, text=h, font=(config.FONT_FAMILY, 11, "bold"), text_color=config.COLOR_TEXT_MUTED)
            lbl.grid(row=0, column=idx, sticky="w", padx=10, pady=4)
        hdr_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        records = self.db.get_attendance_history(date_str=today_date)
        if not records:
            empty_lbl = ctk.CTkLabel(
                self.scroll_table,
                text="No attendance records logged for today yet.",
                font=(config.FONT_FAMILY, 12, "italic"),
                text_color=config.COLOR_TEXT_MUTED
            )
            empty_lbl.pack(pady=20)
            return

        for r in records[:15]:
            row_frame = ctk.CTkFrame(self.scroll_table, fg_color="#162032", height=32)
            row_frame.pack(fill="x", pady=2)
            row_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

            status_color = config.COLOR_SUCCESS if r['status'] == 'P' else config.COLOR_WARNING
            vals = [
                r['roll_no'],
                r['name'],
                r['department'],
                r['time'],
                "PRESENT" if r['status'] == 'P' else "LATE",
                f"{int(r['confidence'] * 100)}%"
            ]
            for idx, v in enumerate(vals):
                tc = status_color if idx == 4 else config.COLOR_TEXT_PRIMARY
                lbl = ctk.CTkLabel(row_frame, text=str(v), font=(config.FONT_FAMILY, 11, "normal" if idx!=4 else "bold"), text_color=tc)
                lbl.grid(row=0, column=idx, sticky="w", padx=10, pady=4)
