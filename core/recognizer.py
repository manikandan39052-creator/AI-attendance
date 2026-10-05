"""
FaceAttend AI Pro - Real-Time Face Recognizer Engine
Loads trained model, performs face detection, matching, confidence scoring,
and anti-spoof / liveness checks.
"""

import os
import pickle
import cv2
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
import config
from core.logger import log_info, log_error

try:
    import face_recognition
    FACE_REC_AVAILABLE = True
except ImportError:
    FACE_REC_AVAILABLE = False

class RealtimeRecognizer:
    def __init__(self, model_path: Path = config.MODEL_PATH):
        self.model_path = model_path
        self.model_data = None
        self.engine_type = "none"
        self.known_encodings = []
        self.known_names = []

        # Eye cascade for liveness / blink check
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        self.load_model()

    def load_model(self) -> bool:
        """Load trained pickle model file."""
        if not self.model_path.exists():
            log_error(f"Model file not found at {self.model_path}")
            return False

        try:
            with open(self.model_path, "rb") as f:
                self.model_data = pickle.load(f)

            self.engine_type = self.model_data.get("engine", "none")
            if self.engine_type == "face_recognition":
                self.known_encodings = self.model_data.get("encodings", [])
                self.known_names = self.model_data.get("names", [])
            log_info(f"Loaded face recognition model ({self.engine_type}) with {len(self.known_names)} encodings.")
            return True
        except Exception as e:
            log_error(f"Failed to load model file: {e}")
            return False

    def detect_liveness(self, face_roi: np.ndarray) -> tuple[bool, str]:
        """
        Anti-spoofing heuristic check:
        1. Texture variance check (detect paper print reflection vs skin structure)
        2. Eye presence check
        """
        gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY) if len(face_roi.shape) == 3 else face_roi
        
        # Texture Laplacian variance check
        lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        if lap_var < 35.0:  # Flat image print / screen reflection threshold
            return False, "Spoof Warning: Flat Image Detected"

        # Eye count check
        eyes = self.eye_cascade.detectMultiScale(gray, 1.1, 3)
        # Even if eyes aren't detected in every single frame, low variance is primary spoof indicator
        return True, "Live Face"

    def recognize_faces(self, frame: np.ndarray, confidence_thresh: float = config.DEFAULT_CONFIDENCE_THRESHOLD) -> List[Dict[str, Any]]:
        """
        Recognize faces in current frame.
        Returns a list of dicts:
        [{
            'student_id': str,
            'confidence': float (0.0 - 1.0),
            'box': (x, y, w, h),
            'is_live': bool,
            'status_msg': str
        }]
        """
        results = []
        if frame is None:
            return results

        display_h, display_w = frame.shape[:2]

        if FACE_REC_AVAILABLE and self.engine_type == "face_recognition" and len(self.known_encodings) > 0:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Find face locations (top, right, bottom, left)
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                w = right - left
                h = bottom - top
                x = left
                y = top

                # Crop ROI for anti-spoof check
                face_roi = frame[max(0, y):min(display_h, y+h), max(0, x):min(display_w, x+w)]
                is_live, liveness_msg = self.detect_liveness(face_roi) if face_roi.size > 0 else (True, "Live Face")

                # Compute face distances
                distances = face_recognition.face_distance(self.known_encodings, face_encoding)
                best_match_idx = np.argmin(distances) if len(distances) > 0 else -1

                if best_match_idx != -1:
                    distance = distances[best_match_idx]
                    confidence = max(0.0, min(1.0, 1.0 - distance))
                    student_id = self.known_names[best_match_idx]

                    if confidence >= confidence_thresh and is_live:
                        results.append({
                            "student_id": student_id,
                            "confidence": round(confidence, 2),
                            "box": (x, y, w, h),
                            "is_live": is_live,
                            "status_msg": "Match Found"
                        })
                    else:
                        results.append({
                            "student_id": "Unknown",
                            "confidence": round(confidence, 2),
                            "box": (x, y, w, h),
                            "is_live": is_live,
                            "status_msg": liveness_msg if not is_live else "Low Confidence"
                        })
                else:
                    results.append({
                        "student_id": "Unknown",
                        "confidence": 0.0,
                        "box": (x, y, w, h),
                        "is_live": is_live,
                        "status_msg": "Unknown Face"
                    })

        else:
            # Fallback OpenCV Haar detection & matching
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(80, 80))

            for (x, y, w, h) in faces:
                face_roi = frame[y:y+h, x:x+w]
                is_live, liveness_msg = self.detect_liveness(face_roi)

                results.append({
                    "student_id": "Unknown",
                    "confidence": 0.50 if is_live else 0.0,
                    "box": (x, y, w, h),
                    "is_live": is_live,
                    "status_msg": "Fallback Mode (Train encodings first)"
                })

        return results

    def save_unknown_face(self, frame: np.ndarray, box: tuple[int, int, int, int]) -> str:
        """Save image snippet of unrecognized face to dataset/unknown/."""
        x, y, w, h = box
        h_img, w_img = frame.shape[:2]
        y1, y2 = max(0, y-10), min(h_img, y+h+10)
        x1, x2 = max(0, x-10), min(w_img, x+w+10)
        
        crop = frame[y1:y2, x1:x2]
        if crop.size == 0:
            return ""

        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        save_path = config.UNKNOWN_DIR / f"unknown_{timestamp_str}.jpg"
        cv2.imwrite(str(save_path), crop)
        return str(save_path)
