"""
FaceAttend AI Pro - Attendance Rule Engine
Applies shift window checks, late penalties, and duplicate attendance prevention.
"""

from datetime import datetime
from typing import Dict, Any, Tuple
import config
from core.database import DatabaseManager
from core.logger import log_info, log_warning

class AttendanceManager:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def check_time_window(self) -> Tuple[bool, str, str]:
        """
        Check current time against configured attendance windows.
        Returns: (is_allowed, status_code ['P'/'L'], display_message)
        """
        now = datetime.now()
        current_time_str = now.strftime("%H:%M")

        start_time = self.db.get_setting("attendance_start", config.DEFAULT_ATTENDANCE_START)
        late_time = self.db.get_setting("late_threshold", config.DEFAULT_LATE_THRESHOLD)
        end_time = self.db.get_setting("attendance_end", config.DEFAULT_ATTENDANCE_END)

        if current_time_str < start_time:
            return False, "", f"Attendance Closed (Opens at {start_time})"
        elif current_time_str > end_time:
            return False, "", f"Attendance Closed for Today (Ended at {end_time})"

        if current_time_str <= late_time:
            return True, "P", "On Time (Present)"
        else:
            return True, "L", "Late Attendance Marked"

    def process_student_recognition(self, student_id: str, confidence: float) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Process a recognized student:
        1. Check duplicate attendance for today.
        2. Check time window rule.
        3. Insert record into Database and update Excel workbook.
        """
        today_date = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H:%M:%S")

        # 1. Fetch student info
        student = self.db.get_student(student_id)
        if not student:
            return False, f"Student record for ID '{student_id}' not found.", {}

        # 2. Check if already marked today
        if self.db.is_attendance_marked_today(student_id, today_date):
            return False, f"Attendance already marked today for {student['name']}.", student

        # 3. Check time window
        is_allowed, status_code, window_msg = self.check_time_window()
        if not is_allowed:
            return False, f"Cannot mark attendance: {window_msg}", student

        # 4. Save to Database
        success = self.db.mark_attendance(
            student_id=student_id,
            date_str=today_date,
            time_str=current_time,
            status=status_code,
            confidence=confidence
        )

        if success:
            log_info(f"Attendance marked for {student['name']} ({student['roll_no']}) - Status: {status_code}")
            return True, f"Welcome {student['name']}, attendance marked ({status_code})!", student
        else:
            return False, f"Database record failed for {student['name']}.", student
