# FaceAttend AI Pro ⚡
> **AI Powered Smart Face Recognition Attendance Management System**

[![Platform](https://img.shields.io/badge/Platform-Windows-blue.svg)](https://microsoft.com)
[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://python.org)
[![GUI](https://img.shields.io/badge/GUI-CustomTkinter-06B6D4.svg)](https://github.com/TomSchimansky/CustomTkinter)
[![Computer Vision](https://img.shields.io/badge/Vision-OpenCV%20%7C%20face__recognition-10B981.svg)](https://opencv.org)

**FaceAttend AI Pro** is a modern, enterprise-grade AI facial recognition attendance management desktop application designed for Schools, Colleges, Universities, Training Institutes, and Enterprise Companies. Built with Python 3.12+, CustomTkinter (Dark Cyber Blue UI design), OpenCV, dlib/face_recognition encodings, SQLite3, OpenPyXL/Pandas, and Matplotlib.

---

## 🌟 Key Features

* **🔒 Secure Admin Authentication**: Multi-admin login screen with SHA-256 password hashing, show password toggling, and remember-me state.
* **📊 Modern Admin Dashboard**: Live KPI cards (Total Students, Present Today, Absent Today, Attendance Rate %), live clock, camera status telemetry, quick action toolbar, and real-time attendance activity log table.
* **👤 Student Registration & Facial Dataset Enrollment**:
  * Form fields with full validation (Student ID, Roll No, Name, Dept, Course, Year, Semester, Section, Gender, Phone, Email, Address, Parent Info, DOB, Blood Group, Admission No).
  * Prevents duplicate Student IDs and Roll Numbers.
  * Automated 100-sample facial image capture with real-time quality filters (Brightness check, Blur Laplacian variance check, Distance check).
* **🧠 AI Face Recognition Trainer**:
  * Extracts 128D deep face embeddings (or OpenCV LBPH histograms fallback).
  * Real-time training progress bar, ETA estimation, faces counter, and interactive terminal log box.
  * Persists trained models to `trainer/face_model.pkl`.
* **🎥 Real-Time Facial Attendance & Anti-Spoofing**:
  * Threaded OpenCV camera stream (30+ FPS smooth UI).
  * Multi-face detection and match confidence percentage.
  * Eye blink & texture variance liveness check (anti-photo spoofing).
  * Automatic single attendance record per day rule (prevents duplicate marking).
  * Automatic unknown face detection & snippet capture (`dataset/unknown/`).
  * Text-to-Speech audio welcome announcements ("Welcome <Student Name>, attendance marked.").
* **📗 Automated Excel Monthly Workbooks**:
  * Automatically creates dynamic monthly sheets (e.g. `January-2027`).
  * Auto-generates columns for all days of the month (01..31) + summary columns (`Present`, `Absent`, `Late`, `%`).
  * Color-coded openpyxl formatting (Green for Present, Yellow for Late, Red for Absent).
* **📈 Visual Analytics & Reports**:
  * Matplotlib graphic visualizer: Department breakdown bar chart and attendance pie chart.
  * One-click export to PDF (ReportLab formatted report), CSV, and Excel.
* **⚙️ System Settings & Backups**:
  * Adjust camera source index, recognition match confidence threshold (40% - 90%), shift attendance window times, and voice toggle.
  * Manual and automated timestamped SQLite database backups with instant restore capability.

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **GUI Framework** | CustomTkinter (Dark Cyber Blue Theme), ttkbootstrap, Pillow |
| **Computer Vision / AI** | OpenCV (`cv2`), `face_recognition` (dlib 128D encodings), NumPy |
| **Database** | SQLite3 (Indexed, Foreign Keys, Parameterized Queries) |
| **Excel Automation** | OpenPyXL, Pandas |
| **Analytics & Reports** | Matplotlib, ReportLab (PDF Generation) |
| **Audio Engine** | `pyttsx3` (Threaded Speech Engine) |

---

## 📁 Directory Structure

```
FaceAttendAI/
├── main.py                     # Primary Application Entrypoint
├── config.py                   # System Configuration, Palette Tokens & Directory Paths
├── requirements.txt            # Python Dependencies
├── README.md                   # Application Documentation
├── seed_sample_data.py         # Sample Dataset & DB Initialization Script
├── build_exe.py                # PyInstaller Packaging Automation Script
│
├── core/                       # Backend Business Logic & AI Engines
│   ├── logger.py               # Rotating Logging Manager
│   ├── database.py             # SQLite Database Manager & CRUD Interface
│   ├── camera.py               # Threaded Non-Blocking OpenCV Camera Stream
│   ├── capture.py              # Face Dataset Quality Evaluation & Capture Engine
│   ├── training.py             # Model Trainer (128D Encodings / LBPH Persistence)
│   ├── recognizer.py           # Real-Time Face Recognizer & Anti-Spoof Engine
│   ├── attendance_manager.py   # Shift Rules, Window Constraints & Duplicate Check
│   ├── excel_manager.py        # Monthly Workbook & Sheet Auto-Formatting
│   ├── report_generator.py     # Matplotlib Charts, PDF, CSV Report Generator
│   ├── voice.py                # Threaded Pyttsx3 Speech Engine
│   ├── utils.py                # Validation, Security Hashing & Image Helpers
│   └── backup.py               # SQLite Backup & Restore Manager
│
├── ui/                         # CustomTkinter Views & Desktop Components
│   ├── app.py                  # Main Window Controller & Navigation Manager
│   ├── login.py                # Admin Authentication View
│   ├── dashboard.py            # Admin Telemetry & Quick Action Dashboard
│   ├── register.py             # Student Registration & Camera Capture View
│   ├── train.py                # AI Model Training & Visual Log Screen
│   ├── attendance.py           # Real-Time Facial Attendance Feed View
│   ├── students.py             # Student Record Management & Search Table
│   ├── reports.py              # Visual Analytics & Report Export Center
│   ├── settings.py             # Camera, Confidence & Backup Configuration
│   └── about.py                # System Diagnostics & Metadata View
│
├── database/                   # SQLite database storage (students.db)
├── dataset/                    # Face image dataset (dataset/<StudentID>/1.jpg..100.jpg)
├── trainer/                    # Trained model storage (face_model.pkl)
├── attendance/                 # Monthly workbooks (Attendance.xlsx)
├── reports/                    # Generated charts and PDF reports
├── exports/                    # Exported CSV / Excel data files
├── logs/                       # System log files (app.log)
└── backups/                    # Automated and manual database snapshots (.db)
```

---

## 🗄️ Database Schema

### `students`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `student_id` | TEXT | PRIMARY KEY | Unique Student ID |
| `roll_no` | TEXT | UNIQUE, NOT NULL | Institution Roll Number |
| `name` | TEXT | NOT NULL | Student Full Name |
| `department` | TEXT | NOT NULL | Academic Department |
| `course` | TEXT | | Degree / Program |
| `year` | TEXT | | Academic Year |
| `semester` | TEXT | | Current Semester |
| `section` | TEXT | | Class Section |
| `gender` | TEXT | | Gender |
| `phone` | TEXT | | Contact Phone Number |
| `email` | TEXT | | Student Email Address |
| `address` | TEXT | | Residential Address |
| `parent_name` | TEXT | | Parent / Guardian Name |
| `parent_phone` | TEXT | | Parent Phone Number |
| `blood_group` | TEXT | | Blood Group |
| `dob` | TEXT | | Date of Birth |
| `admission_no` | TEXT | | Institutional Admission No |
| `photo_path` | TEXT | | Path to primary facial image |

### `attendance`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Record ID |
| `student_id` | TEXT | FOREIGN KEY -> students | Student FK |
| `date` | TEXT | NOT NULL | Attendance Date (YYYY-MM-DD) |
| `time` | TEXT | NOT NULL | Timestamp (HH:MM:SS) |
| `status` | TEXT | NOT NULL | Status ('P' Present, 'L' Late) |
| `confidence` | REAL | | AI Match Confidence (0.0 - 1.0) |
| `UNIQUE(student_id, date)` | | | Prevents duplicate daily marking |

---

## 🚀 Quick Start Guide

### Prerequisites
* Windows 10 / 11 (64-bit)
* Python 3.12+ installed and added to PATH
* Webcam connected to computer

### Installation
1. Open PowerShell or Command Prompt:
   ```cmd
   cd "d:\ai attendance"
   ```
2. Install dependencies:
   ```cmd
   pip install -r requirements.txt
   ```
3. Seed sample dataset and initialize database:
   ```cmd
   python seed_sample_data.py
   ```
4. Run application:
   ```cmd
   python main.py
   ```

### Default Login Credentials
* **Username**: `admin`
* **Password**: `admin123`

---

## 📦 PyInstaller EXE Packaging

To package **FaceAttend AI Pro** into a single executable folder for distribution:

1. Run the included build script:
   ```cmd
   python build_exe.py
   ```
2. Locate the generated executable at:
   `dist\FaceAttend_AI_Pro\FaceAttend_AI_Pro.exe`

---

## ❓ Troubleshooting & FAQ

* **Q: Camera screen remains black or fails to open.**
  * *A*: Navigate to **Settings**, change the **Camera Source Index** from `0` to `1` or `2`, and click **Save Configuration Settings**.
* **Q: `face_recognition` / `dlib` installation errors on Windows.**
  * *A*: FaceAttend AI Pro automatically detects whether `face_recognition` is installed. If not, it gracefully fallback to OpenCV's built-in facial detection engine.
* **Q: Duplicate attendance was not marked.**
  * *A*: The system deliberately prevents marking attendance more than once per day for the same student.

---

## 📄 License & Credits

Designed & Developed by **Apex AI Systems**.  
Built with Python 3.12, CustomTkinter, OpenCV, and OpenPyXL.
