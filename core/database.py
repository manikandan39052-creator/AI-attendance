"""
FaceAttend AI Pro - Database Manager
Handles SQLite connection, schema migrations, indexing, and CRUD queries.
"""

import sqlite3
import os
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
import config
from core.logger import log_info, log_error
from core.utils import hash_password

class DatabaseManager:
    def __init__(self, db_path: str = str(config.DATABASE_PATH)):
        self.db_path = db_path
        self.init_database()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def init_database(self):
        """Create required tables, indexes, and default seed data if not present."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # 1. Admins Table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS admins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    email TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """)

                # 2. Students Table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    student_id TEXT PRIMARY KEY,
                    roll_no TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    department TEXT NOT NULL,
                    course TEXT,
                    year TEXT,
                    semester TEXT,
                    section TEXT,
                    gender TEXT,
                    phone TEXT,
                    email TEXT,
                    address TEXT,
                    parent_name TEXT,
                    parent_phone TEXT,
                    blood_group TEXT,
                    dob TEXT,
                    admission_no TEXT,
                    photo_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """)

                # 3. Attendance Table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT NOT NULL,
                    date TEXT NOT NULL,
                    time TEXT NOT NULL,
                    status TEXT NOT NULL,
                    confidence REAL DEFAULT 0.0,
                    camera_id INTEGER DEFAULT 0,
                    FOREIGN KEY (student_id) REFERENCES students (student_id) ON DELETE CASCADE,
                    UNIQUE(student_id, date)
                );
                """)

                # 4. Unknown Faces Table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS unknown_faces (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    image_path TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    camera_id INTEGER DEFAULT 0
                );
                """)

                # 5. System Settings Table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                """)

                # 6. System Logs Table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """)

                # Indexes for query speed
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_students_roll ON students(roll_no);")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_students_dept ON students(department);")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_attendance_date ON attendance(date);")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_attendance_student ON attendance(student_id);")

                # Default Admin Seed
                cursor.execute("SELECT COUNT(*) FROM admins;")
                if cursor.fetchone()[0] == 0:
                    default_pass = hash_password("admin123")
                    cursor.execute(
                        "INSERT INTO admins (username, password_hash, email) VALUES (?, ?, ?);",
                        ("admin", default_pass, "admin@faceattend.ai")
                    )
                    log_info("Default admin account created (admin / admin123).")

                # Default Settings Seed
                default_settings = {
                    "camera_index": str(config.DEFAULT_CAMERA_INDEX),
                    "confidence_threshold": str(config.DEFAULT_CONFIDENCE_THRESHOLD),
                    "voice_enabled": "1" if config.DEFAULT_VOICE_ENABLED else "0",
                    "attendance_start": config.DEFAULT_ATTENDANCE_START,
                    "late_threshold": config.DEFAULT_LATE_THRESHOLD,
                    "attendance_end": config.DEFAULT_ATTENDANCE_END,
                    "auto_backup": "1" if config.DEFAULT_AUTO_BACKUP else "0",
                    "theme": config.THEME_MODE
                }
                for key, val in default_settings.items():
                    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?);", (key, val))

                conn.commit()
                log_info("Database initialized successfully.")
        except Exception as e:
            log_error(f"Database initialization error: {e}", exc_info=True)
            raise e

    # --- ADMIN FUNCTIONS ---
    def verify_admin(self, username: str, password_raw: str) -> bool:
        """Verify admin login credentials."""
        pass_hash = hash_password(password_raw)
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM admins WHERE username = ? AND password_hash = ?;", (username, pass_hash))
            return cursor.fetchone() is not None

    def update_admin_password(self, username: str, new_password_raw: str) -> bool:
        pass_hash = hash_password(new_password_raw)
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE admins SET password_hash = ? WHERE username = ?;", (pass_hash, username))
            conn.commit()
            return cursor.rowcount > 0

    # --- STUDENT CRUD FUNCTIONS ---
    def add_student(self, data: Dict[str, Any]) -> bool:
        """Add a new student record to the database."""
        sql = """
        INSERT INTO students (
            student_id, roll_no, name, department, course, year, semester, section,
            gender, phone, email, address, parent_name, parent_phone, blood_group,
            dob, admission_no, photo_path
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        params = (
            data['student_id'], data['roll_no'], data['name'], data['department'],
            data.get('course', ''), data.get('year', ''), data.get('semester', ''),
            data.get('section', ''), data.get('gender', ''), data.get('phone', ''),
            data.get('email', ''), data.get('address', ''), data.get('parent_name', ''),
            data.get('parent_phone', ''), data.get('blood_group', ''), data.get('dob', ''),
            data.get('admission_no', ''), data.get('photo_path', '')
        )
        try:
            with self.get_connection() as conn:
                conn.cursor().execute(sql, params)
                conn.commit()
                return True
        except sqlite3.IntegrityError as e:
            log_error(f"Student insert integrity error: {e}")
            return False

    def update_student(self, student_id: str, data: Dict[str, Any]) -> bool:
        """Update an existing student record."""
        sql = """
        UPDATE students SET
            roll_no=?, name=?, department=?, course=?, year=?, semester=?, section=?,
            gender=?, phone=?, email=?, address=?, parent_name=?, parent_phone=?,
            blood_group=?, dob=?, admission_no=?
        WHERE student_id=?;
        """
        params = (
            data['roll_no'], data['name'], data['department'], data.get('course', ''),
            data.get('year', ''), data.get('semester', ''), data.get('section', ''),
            data.get('gender', ''), data.get('phone', ''), data.get('email', ''),
            data.get('address', ''), data.get('parent_name', ''), data.get('parent_phone', ''),
            data.get('blood_group', ''), data.get('dob', ''), data.get('admission_no', ''),
            student_id
        )
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
            return cursor.rowcount > 0

    def delete_student(self, student_id: str) -> bool:
        """Delete a student and cascade delete attendance logs."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM students WHERE student_id = ?;", (student_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_student(self, student_id: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students WHERE student_id = ?;", (student_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_all_students(self, department: str = "All", search_query: str = "") -> List[Dict[str, Any]]:
        """Fetch student records with optional search query and department filter."""
        sql = "SELECT * FROM students WHERE 1=1"
        params = []
        if department and department != "All":
            sql += " AND department = ?"
            params.append(department)
        if search_query:
            sql += " AND (name LIKE ? OR roll_no LIKE ? OR student_id LIKE ? OR email LIKE ?)"
            q = f"%{search_query}%"
            params.extend([q, q, q, q])
        sql += " ORDER BY name ASC;"

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            return [dict(row) for row in cursor.fetchall()]

    def is_student_id_exists(self, student_id: str) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM students WHERE student_id = ?;", (student_id,))
            return cursor.fetchone() is not None

    def is_roll_no_exists(self, roll_no: str) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM students WHERE roll_no = ?;", (roll_no,))
            return cursor.fetchone() is not None

    # --- ATTENDANCE FUNCTIONS ---
    def mark_attendance(self, student_id: str, date_str: str, time_str: str, status: str, confidence: float = 0.0) -> bool:
        """Insert attendance record. Ignores if already marked today for this student."""
        sql = """
        INSERT INTO attendance (student_id, date, time, status, confidence)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(student_id, date) DO NOTHING;
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (student_id, date_str, time_str, status, confidence))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            log_error(f"Error marking attendance for {student_id}: {e}")
            return False

    def is_attendance_marked_today(self, student_id: str, date_str: str) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM attendance WHERE student_id = ? AND date = ?;", (student_id, date_str))
            return cursor.fetchone() is not None

    def get_attendance_history(self, date_str: str = "", department: str = "All", student_search: str = "") -> List[Dict[str, Any]]:
        """Fetch detailed attendance records joined with student information."""
        sql = """
        SELECT a.id, a.student_id, s.roll_no, s.name, s.department, a.date, a.time, a.status, a.confidence
        FROM attendance a
        JOIN students s ON a.student_id = s.student_id
        WHERE 1=1
        """
        params = []
        if date_str:
            sql += " AND a.date = ?"
            params.append(date_str)
        if department and department != "All":
            sql += " AND s.department = ?"
            params.append(department)
        if student_search:
            sql += " AND (s.name LIKE ? OR s.roll_no LIKE ? OR s.student_id LIKE ?)"
            q = f"%{student_search}%"
            params.extend([q, q, q])
        sql += " ORDER BY a.date DESC, a.time DESC;"

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            return [dict(row) for row in cursor.fetchall()]

    def record_unknown_face(self, image_path: str, timestamp: str):
        with self.get_connection() as conn:
            conn.cursor().execute(
                "INSERT INTO unknown_faces (image_path, timestamp) VALUES (?, ?);",
                (image_path, timestamp)
            )
            conn.commit()

    # --- SETTINGS FUNCTIONS ---
    def get_setting(self, key: str, default_val: str = "") -> str:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = ?;", (key,))
            row = cursor.fetchone()
            return row['value'] if row else default_val

    def set_setting(self, key: str, value: str):
        with self.get_connection() as conn:
            conn.cursor().execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?);", (key, value))
            conn.commit()

    def get_all_settings(self) -> Dict[str, str]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM settings;")
            return {row['key']: row['value'] for row in cursor.fetchall()}

    # --- DASHBOARD & ANALYTICS STATS ---
    def get_dashboard_stats(self, date_str: str) -> Dict[str, Any]:
        """Fetch real-time metrics for Dashboard display."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total Students
            cursor.execute("SELECT COUNT(*) FROM students;")
            total_students = cursor.fetchone()[0]

            # Present Today
            cursor.execute("SELECT COUNT(*) FROM attendance WHERE date = ? AND (status = 'P' OR status = 'L');", (date_str,))
            present_today = cursor.fetchone()[0]

            # Late Today
            cursor.execute("SELECT COUNT(*) FROM attendance WHERE date = ? AND status = 'L';", (date_str,))
            late_today = cursor.fetchone()[0]

            absent_today = max(0, total_students - present_today)
            attendance_pct = (present_today / total_students * 100.0) if total_students > 0 else 0.0

            return {
                "total_students": total_students,
                "present_today": present_today,
                "absent_today": absent_today,
                "late_today": late_today,
                "attendance_percentage": round(attendance_pct, 1)
            }

    def get_department_stats(self, date_str: str) -> List[Tuple[str, int, int]]:
        """Returns List of (department, present_count, total_count) for date."""
        sql = """
        SELECT 
            s.department,
            COUNT(DISTINCT s.student_id) as total_dept_students,
            COUNT(DISTINCT a.student_id) as present_dept_students
        FROM students s
        LEFT JOIN attendance a ON s.student_id = a.student_id AND a.date = ?
        GROUP BY s.department;
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (date_str,))
            return [(row['department'], row['present_dept_students'], row['total_dept_students']) for row in cursor.fetchall()]
