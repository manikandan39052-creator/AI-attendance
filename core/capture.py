"""
FaceAttend AI Pro - Face Dataset Capture Engine
Captures face images with real-time brightness, blur, and face quality checks.
"""

import cv2
import os
import numpy as np
from pathlib import Path
import config
from core.logger import log_info, log_error

class FaceCaptureManager:
    def __init__(self):
        # Haar cascade face detector
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

    def evaluate_frame_quality(self, frame: np.ndarray, face_box: tuple[int, int, int, int]) -> tuple[bool, str]:
        """
        Evaluate face frame quality:
        1. Brightness check
        2. Blur check via Laplacian variance
        3. Face size check
        """
        x, y, w, h = face_box
        if w < 100 or h < 100:
            return False, "Too Far - Move Closer"

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_roi = gray[y:y+h, x:x+w]

        # Brightness Check
        mean_brightness = np.mean(face_roi)
        if mean_brightness < config.MIN_QUALITY_BRIGHTNESS:
            return False, "Too Dark - Increase Lighting"

        # Blur Check (Laplacian Variance)
        laplacian_var = cv2.Laplacian(face_roi, cv2.CV_64F).var()
        if laplacian_var < config.MIN_QUALITY_BLUR_VAR:
            return False, f"Blurry ({int(laplacian_var)}) - Hold Still"

        return True, "Good Quality"

    def process_and_save_face(
        self,
        frame: np.ndarray,
        student_id: str,
        sample_count: int,
        target_total: int = config.DEFAULT_DATASET_SAMPLE_COUNT
    ) -> tuple[bool, str, np.ndarray, int]:
        """
        Detect face, evaluate quality, and save image to dataset/<student_id>/.
        Returns (success, status_msg, processed_frame, updated_count).
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(80, 80)
        )

        display_frame = frame.copy()

        if len(faces) == 0:
            return False, "No Face Detected", display_frame, sample_count
        if len(faces) > 1:
            return False, "Multiple Faces Detected", display_frame, sample_count

        x, y, w, h = faces[0]
        is_valid, msg = self.evaluate_frame_quality(frame, (x, y, w, h))

        # Color indicator: Green if valid, Amber if invalid
        color = (16, 185, 129) if is_valid else (245, 158, 11)
        cv2.rectangle(display_frame, (x, y), (x + w, y + h), color, 2)
        cv2.putText(
            display_frame,
            f"{msg} ({sample_count}/{target_total})",
            (x, max(20, y - 10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            color,
            2
        )

        if is_valid and sample_count < target_total:
            student_dir = config.DATASET_DIR / student_id
            os.makedirs(student_dir, exist_ok=True)

            # Crop face with padding
            pad = 20
            h_img, w_img = frame.shape[:2]
            y1 = max(0, y - pad)
            y2 = min(h_img, y + h + pad)
            x1 = max(0, x - pad)
            x2 = min(w_img, x + w + pad)

            face_img = frame[y1:y2, x1:x2]
            face_img_resized = cv2.resize(face_img, (200, 200))

            sample_count += 1
            save_path = student_dir / f"{sample_count}.jpg"
            cv2.imwrite(str(save_path), face_img_resized)

            return True, f"Saved Sample {sample_count}/{target_total}", display_frame, sample_count

        return False, msg, display_frame, sample_count
