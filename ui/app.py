"""
FaceAttend AI Pro - Main UI Window Controller
Handles sidebar navigation, top header, page switching, and animated toast notifications.
"""

import customtkinter as ctk
import config
from core.database import DatabaseManager
from ui.login import LoginView
from ui.dashboard import DashboardView
from ui.register import RegisterView
from ui.train import TrainView
from ui.attendance import AttendanceView
from ui.students import StudentsView
from ui.reports import ReportsView
from ui.settings import SettingsView
from ui.about import AboutView

class MainApplication(ctk.CTk):
    def __init__(self, db: DatabaseManager):
        super().__init__()
        self.db = db

        # Window Config
        self.title(f"{config.APP_NAME} - {config.APP_TAGLINE}")
        self.geometry("1280x780")
        self.minsize(1080, 680)

        # Set CustomTkinter Theme
        ctk.set_appearance_mode(config.THEME_MODE)
        ctk.set_default_color_theme(config.THEME_COLOR_SCHEME)
        self.configure(fg_color=config.COLOR_BG)

        self.is_authenticated = False
        self.current_route = "login"
        self.views = {}

        self._build_layout()
        self.show_login()

    def _build_layout(self):
        # Configure root grid
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # 1. TOP HEADER BAR
        self.header_frame = ctk.CTkFrame(self, fg_color=config.COLOR_SIDEBAR, height=54, corner_radius=0)
        self.header_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.header_frame.grid_propagate(False)

        top_logo = ctk.CTkLabel(
            self.header_frame,
            text="⚡ FACEATTEND AI PRO",
            font=(config.FONT_FAMILY, 16, "bold"),
            text_color=config.COLOR_PRIMARY
        )
        top_logo.pack(side="left", padx=20)

        tagline_lbl = ctk.CTkLabel(
            self.header_frame,
            text="AI Powered Attendance System",
            font=(config.FONT_FAMILY, 11, "italic"),
            text_color=config.COLOR_TEXT_MUTED
        )
        tagline_lbl.pack(side="left", padx=5)

        self.logout_btn = ctk.CTkButton(
            self.header_frame,
            text="🔒 Logout",
            width=80,
            height=30,
            fg_color=config.COLOR_DANGER,
            font=(config.FONT_FAMILY, 11, "bold"),
            command=self.logout
        )
        self.logout_btn.pack(side="right", padx=20)
        self.logout_btn.pack_forget()  # Hidden initially until logged in

        # 2. LEFT NAVIGATION SIDEBAR
        self.sidebar = ctk.CTkFrame(self, fg_color=config.COLOR_SIDEBAR, width=220, corner_radius=0)
        self.sidebar.grid(row=1, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # 3. MAIN CONTENT DISPLAY FRAME
        self.container = ctk.CTkFrame(self, fg_color=config.COLOR_BG, corner_radius=0)
        self.container.grid(row=1, column=1, sticky="nsew")

    def show_login(self):
        self.is_authenticated = False
        self.sidebar.grid_remove()
        self.logout_btn.pack_forget()

        # Clear container
        for child in self.container.winfo_children():
            child.destroy()

        login_view = LoginView(self.container, self.db, on_login_success=self.on_login_success)
        login_view.pack(fill="both", expand=True)

    def on_login_success(self):
        self.is_authenticated = True
        self.sidebar.grid(row=1, column=0, sticky="nsew")
        self.logout_btn.pack(side="right", padx=20)
        self._build_sidebar_menu()
        self.navigate_to("dashboard")

    def _build_sidebar_menu(self):
        for child in self.sidebar.winfo_children():
            child.destroy()

        nav_header = ctk.CTkLabel(
            self.sidebar,
            text="NAVIGATION MENU",
            font=(config.FONT_FAMILY, 10, "bold"),
            text_color=config.COLOR_TEXT_MUTED
        )
        nav_header.pack(anchor="w", padx=20, pady=(20, 10))

        nav_items = [
            ("📊 Dashboard", "dashboard"),
            ("👤 Register Student", "register"),
            ("🧠 Train Model", "train"),
            ("🎥 Start Attendance", "attendance"),
            ("📋 Student Records", "students"),
            ("📊 Reports & Export", "reports"),
            ("⚙️ System Settings", "settings"),
            ("ℹ️ About App", "about")
        ]

        self.nav_buttons = {}
        for text, route in nav_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                font=(config.FONT_FAMILY, 12, "bold"),
                fg_color="transparent",
                text_color=config.COLOR_TEXT_PRIMARY,
                hover_color=config.COLOR_CARD_HOVER,
                anchor="w",
                height=40,
                corner_radius=8,
                command=lambda r=route: self.navigate_to(r)
            )
            btn.pack(fill="x", padx=12, pady=3)
            self.nav_buttons[route] = btn

    def navigate_to(self, route: str):
        if not self.is_authenticated and route != "login":
            return

        self.current_route = route

        # Highlight active nav button
        for r, btn in self.nav_buttons.items():
            if r == route:
                btn.configure(fg_color=config.COLOR_PRIMARY, text_color="#FFFFFF")
            else:
                btn.configure(fg_color="transparent", text_color=config.COLOR_TEXT_PRIMARY)

        # Clear container
        for child in self.container.winfo_children():
            # Stop any camera feeds before switching view
            if hasattr(child, 'stop_attendance'):
                child.stop_attendance()
            if hasattr(child, '_stop_capture'):
                child._stop_capture()
            child.destroy()

        # Instantiate View
        if route == "dashboard":
            view = DashboardView(self.container, self.db, navigate_callback=self.navigate_to)
        elif route == "register":
            view = RegisterView(self.container, self.db, show_toast=self.show_toast)
        elif route == "train":
            view = TrainView(self.container, self.db, show_toast=self.show_toast)
        elif route == "attendance":
            view = AttendanceView(self.container, self.db, show_toast=self.show_toast)
        elif route == "students":
            view = StudentsView(self.container, self.db, show_toast=self.show_toast)
        elif route == "reports":
            view = ReportsView(self.container, self.db, show_toast=self.show_toast)
        elif route == "settings":
            view = SettingsView(self.container, self.db, show_toast=self.show_toast)
        elif route == "about":
            view = AboutView(self.container)
        else:
            view = DashboardView(self.container, self.db, navigate_callback=self.navigate_to)

        view.pack(fill="both", expand=True)

    def show_toast(self, title: str, message: str):
        """Display non-blocking toast notification banner."""
        toast = ctk.CTkFrame(self, fg_color=config.COLOR_CARD, corner_radius=10, border_width=1, border_color=config.COLOR_PRIMARY)
        toast.place(relx=0.98, rely=0.08, anchor="ne")

        t_title = ctk.CTkLabel(toast, text=title, font=(config.FONT_FAMILY, 12, "bold"), text_color=config.COLOR_PRIMARY)
        t_title.pack(anchor="w", padx=15, pady=(8, 2))

        t_msg = ctk.CTkLabel(toast, text=message, font=(config.FONT_FAMILY, 11), text_color=config.COLOR_TEXT_PRIMARY)
        t_msg.pack(anchor="w", padx=15, pady=(0, 8))

        # Auto dismiss after 3 seconds
        self.after(3500, toast.destroy)

    def logout(self):
        self.show_login()
