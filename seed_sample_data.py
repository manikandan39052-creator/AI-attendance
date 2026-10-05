"""
FaceAttend AI Pro - Seed Sample Data Script
Populates initial sample database records, sample dataset images, and Attendance.xlsx sheet.
"""

import os
import cv2
import numpy as np
from datetime import datetime
import config
from core.database import DatabaseManager
from core.excel_manager import ExcelManager
from core.logger import log_info

def seed_all():
    config.init_directories()
    db = DatabaseManager()

    sample_students = [
        {
            "student_id": "STU1001",
            "roll_no": "2027-CS-01",
            "name": "Alexander Pierce",
            "department": "Computer Science",
            "course": "B.Tech CS",
            "year": "3rd Year",
            "semester": "6th Semester",
            "section": "A",
            "gender": "Male",
            "phone": "+1 555-0192",
            "email": "alex.pierce@university.edu",
            "address": "104 Campus Way, Tech City",
            "parent_name": "Robert Pierce",
            "parent_phone": "+1 555-0199",
            "blood_group": "O+",
            "dob": "2004-05-14",
            "admission_no": "ADM-2024-01",
            "photo_path": str(config.DATASET_DIR / "STU1001" / "1.jpg")
        },
        {
            "student_id": "STU1002",
            "roll_no": "2027-CS-02",
            "name": "Sophia Vance",
            "department": "Computer Science",
            "course": "B.Tech CS",
            "year": "3rd Year",
            "semester": "6th Semester",
            "section": "A",
            "gender": "Female",
            "phone": "+1 555-0193",
            "email": "sophia.vance@university.edu",
            "address": "202 Oak Avenue, Tech City",
            "parent_name": "David Vance",
            "parent_phone": "+1 555-0198",
            "blood_group": "A+",
            "dob": "2004-08-22",
            "admission_no": "ADM-2024-02",
            "photo_path": str(config.DATASET_DIR / "STU1002" / "1.jpg")
        },
        {
            "student_id": "STU1003",
            "roll_no": "2027-EE-01",
            "name": "Marcus Sterling",
            "department": "Electrical Engineering",
            "course": "B.Tech EE",
            "year": "2nd Year",
            "semester": "4th Semester",
            "section": "B",
            "gender": "Male",
            "phone": "+1 555-0194",
            "email": "marcus.sterling@university.edu",
            "address": "45 Innovation Blvd",
            "parent_name": "Elizabeth Sterling",
            "parent_phone": "+1 555-0197",
            "blood_group": "B+",
            "dob": "2005-01-10",
            "admission_no": "ADM-2025-01",
            "photo_path": str(config.DATASET_DIR / "STU1003" / "1.jpg")
        },
        {
            "student_id": "STU1004",
            "roll_no": "2027-ME-01",
            "name": "Elena Rostova",
            "department": "Mechanical Engineering",
            "course": "B.Tech ME",
            "year": "4th Year",
            "semester": "8th Semester",
            "section": "A",
            "gender": "Female",
            "phone": "+1 555-0195",
            "email": "elena.rostova@university.edu",
            "address": "88 Industrial Road",
            "parent_name": "Nikolai Rostov",
            "parent_phone": "+1 555-0196",
            "blood_group": "AB+",
            "dob": "2003-11-30",
            "admission_no": "ADM-2023-05",
            "photo_path": str(config.DATASET_DIR / "STU1004" / "1.jpg")
        },
        {
            "student_id": "STU1005",
            "roll_no": "2027-BA-01",
            "name": "Liam Gallagher",
            "department": "Business Admin",
            "course": "BBA",
            "year": "1st Year",
            "semester": "2nd Semester",
            "section": "C",
            "gender": "Male",
            "phone": "+1 555-0196",
            "email": "liam.gallagher@university.edu",
            "address": "12 Metro Heights",
            "parent_name": "Paul Gallagher",
            "parent_phone": "+1 555-0195",
            "blood_group": "O-",
            "dob": "2006-03-18",
            "admission_no": "ADM-2026-12",
            "photo_path": str(config.DATASET_DIR / "STU1005" / "1.jpg")
        }
    ]

    for s in sample_students:
        if not db.is_student_id_exists(s["student_id"]):
            db.add_student(s)

            # Create synthetic facial dataset sample image
            s_dir = config.DATASET_DIR / s["student_id"]
            os.makedirs(s_dir, exist_ok=True)
            for i in range(1, 11):
                # Generate a dummy synthetic face image matrix
                img = np.full((200, 200, 3), (30, 40, 60), dtype=np.uint8)
                # Draw synthetic face circle & eyes
                cv2.circle(img, (100, 100), 70, (200, 180, 160), -1)
                cv2.circle(img, (80, 85), 10, (50, 50, 50), -1)
                cv2.circle(img, (120, 85), 10, (50, 50, 50), -1)
                cv2.ellipse(img, (100, 130), (25, 12), 0, 0, 180, (50, 50, 50), 3)
                cv2.imwrite(str(s_dir / f"{i}.jpg"), img)

    # Seed initial attendance for today
    today_date = datetime.now().strftime("%Y-%m-%d")
    db.mark_attendance("STU1001", today_date, "08:15:00", "P", 0.95)
    db.mark_attendance("STU1002", today_date, "08:22:00", "P", 0.92)
    db.mark_attendance("STU1003", today_date, "09:30:00", "L", 0.88)

    # Generate Excel Workbook
    excel_mgr = ExcelManager(db)
    excel_mgr.generate_monthly_sheet()

    log_info("Sample dataset and initial attendance records seeded successfully.")

if __name__ == "__main__":
    seed_all()
