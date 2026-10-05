"""
FaceAttend AI Pro - Helper Utilities
Input validation, password hashing, and image conversion tools.
"""

import re
import hashlib
from datetime import datetime
import cv2
from PIL import Image, ImageTk

def validate_email(email: str) -> bool:
    """Validate email address format."""
    if not email:
        return True  # Optional field check handled elsewhere
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email.strip()))

def validate_phone(phone: str) -> bool:
    """Validate phone number (numeric, 7 to 15 digits)."""
    if not phone:
        return True
    pattern = r'^\+?[\d\s-]{7,15}$'
    return bool(re.match(pattern, phone.strip()))

def hash_password(password: str, salt: str = "FaceAttendAI_Salt_2027") -> str:
    """Securely hash a password using SHA-256."""
    data = (password + salt).encode('utf-8')
    return hashlib.sha256(data).hexdigest()

def get_current_date_str() -> str:
    """Get current date as YYYY-MM-DD."""
    return datetime.now().strftime("%Y-%m-%d")

def get_current_time_str() -> str:
    """Get current time as HH:MM:SS."""
    return datetime.now().strftime("%H:%M:%S")

def get_current_month_str() -> str:
    """Get current month string like January-2027."""
    return datetime.now().strftime("%B-%Y")

def cv2_to_pillow(cv_img, size: tuple[int, int] = None):
    """Convert an OpenCV BGR image to PIL Image with optional resize."""
    rgb_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(rgb_img)
    if size:
        pil_img = pil_img.resize(size, Image.Resampling.LANCZOS)
    return pil_img
