"""
FaceAttend AI Pro - Admin Login View
CustomTkinter animated login screen with security validation and dark theme styling.
"""

import customtkinter as ctk
import config
from core.database import DatabaseManager
from core.logger import log_info

class LoginView(ctk.CTkFrame):
    def __init__(self, parent, db: DatabaseManager, on_login_success):
        super().__init__(parent, fg_color=config.COLOR_BG)
        self.db = db
        self.on_login_success = on_login_success

        self._create_widgets()

    def _create_widgets(self):
        # Center Container Card
        card = ctk.CTkFrame(
            self,
            width=420,
            height=480,
            fg_color=config.COLOR_CARD,
            corner_radius=16,
            border_width=1,
            border_color=config.COLOR_BORDER
        )
        card.place(relx=0.5, rely=0.5, anchor="center")

        # Header Badge / Logo
        logo_label = ctk.CTkLabel(
            card,
            text="🔒 FACEATTEND AI PRO",
            font=(config.FONT_FAMILY, 22, "bold"),
            text_color=config.COLOR_PRIMARY
        )
        logo_label.pack(pady=(35, 5))

        subtitle = ctk.CTkLabel(
            card,
            text="Admin Authentication Terminal",
            font=(config.FONT_FAMILY, 12, "normal"),
            text_color=config.COLOR_TEXT_MUTED
        )
        subtitle.pack(pady=(0, 25))

        # Username Input
        self.user_entry = ctk.CTkEntry(
            card,
            placeholder_text="Admin Username",
            width=320,
            height=42,
            corner_radius=8,
            border_color=config.COLOR_BORDER,
            fg_color="#0F172A",
            text_color=config.COLOR_TEXT_PRIMARY
        )
        self.user_entry.pack(pady=10)
        self.user_entry.insert(0, "admin")

        # Password Input
        self.pass_entry = ctk.CTkEntry(
            card,
            placeholder_text="Password",
            show="•",
            width=320,
            height=42,
            corner_radius=8,
            border_color=config.COLOR_BORDER,
            fg_color="#0F172A",
            text_color=config.COLOR_TEXT_PRIMARY
        )
        self.pass_entry.pack(pady=10)
        self.pass_entry.insert(0, "admin123")

        # Options Frame (Show Pass & Remember Me)
        opt_frame = ctk.CTkFrame(card, fg_color="transparent")
        opt_frame.pack(fill="x", padx=50, pady=(5, 15))

        self.show_pass_chk = ctk.CTkCheckBox(
            opt_frame,
            text="Show",
            command=self._toggle_pass_visibility,
            font=(config.FONT_FAMILY, 11),
            text_color=config.COLOR_TEXT_MUTED,
            checkbox_width=18,
            checkbox_height=18
        )
        self.show_pass_chk.pack(side="left")

        self.remember_chk = ctk.CTkCheckBox(
            opt_frame,
            text="Remember Me",
            font=(config.FONT_FAMILY, 11),
            text_color=config.COLOR_TEXT_MUTED,
            checkbox_width=18,
            checkbox_height=18
        )
        self.remember_chk.pack(side="right")

        # Feedback Error Message Label
        self.msg_label = ctk.CTkLabel(
            card,
            text="",
            font=(config.FONT_FAMILY, 11, "bold"),
            text_color=config.COLOR_DANGER
        )
        self.msg_label.pack(pady=(0, 10))

        # Submit Login Button
        login_btn = ctk.CTkButton(
            card,
            text="LOGIN TO DASHBOARD",
            font=(config.FONT_FAMILY, 13, "bold"),
            fg_color=config.COLOR_PRIMARY,
            hover_color=config.COLOR_PRIMARY_HOVER,
            width=320,
            height=44,
            corner_radius=8,
            command=self._handle_login
        )
        login_btn.pack(pady=(0, 20))

        # Footer hint
        footer_lbl = ctk.CTkLabel(
            card,
            text="Default Credentials: admin / admin123",
            font=(config.FONT_FAMILY, 10, "italic"),
            text_color=config.COLOR_TEXT_MUTED
        )
        footer_lbl.pack(pady=(0, 10))

        # Bind Enter key
        self.pass_entry.bind("<Return>", lambda e: self._handle_login())

    def _toggle_pass_visibility(self):
        if self.show_pass_chk.get() == 1:
            self.pass_entry.configure(show="")
        else:
            self.pass_entry.configure(show="•")

    def _handle_login(self):
        username = self.user_entry.get().strip()
        password = self.pass_entry.get()

        if not username or not password:
            self.msg_label.configure(text="Please enter both username and password.", text_color=config.COLOR_WARNING)
            return

        if self.db.verify_admin(username, password):
            log_info(f"Admin login successful for '{username}'.")
            self.msg_label.configure(text="Login successful!", text_color=config.COLOR_SUCCESS)
            self.after(400, self.on_login_success)
        else:
            self.msg_label.configure(text="Invalid Username or Password.", text_color=config.COLOR_DANGER)
