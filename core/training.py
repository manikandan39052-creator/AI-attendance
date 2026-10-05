"""
FaceAttend AI Pro - Face Recognition Model Trainer
Trains facial recognition models using face_recognition encodings or OpenCV LBPH fallback.
Persists model encodings to trainer/face_model.pkl.
"""

import os
import pickle
import time
import cv2
import numpy as np
from pathlib import Path
from typing import Callable, Optional
import config
from core.logger import log_info, log_error

# Optional import of face_recognition library
try:
    import face_recognition
    FACE_REC_AVAILABLE = True
except ImportError:
    FACE_REC_AVAILABLE = False

class ModelTrainer:
    def __init__(self):
        self.dataset_dir = config.DATASET_DIR
        self.model_path = config.MODEL_PATH

    def train_model(self, progress_callback: Optional[Callable[[float, str, int, float], None]] = None) -> tuple[bool, str]:
        """
        Train AI face recognition model on all student images in dataset.
        progress_callback format: callback(progress_pct, current_status, faces_trained, eta_seconds)
        """
        student_dirs = [d for d in self.dataset_dir.iterdir() if d.is_dir() and d.name != "unknown"]
        if not student_dirs:
            return False, "No student dataset folders found in dataset directory."

        total_students = len(student_dirs)
        known_encodings = []
        known_names = []
        student_id_map = {}

        # Collect image files
        image_tasks = []
        for s_dir in student_dirs:
            student_id = s_dir.name
            img_files = list(s_dir.glob("*.jpg")) + list(s_dir.glob("*.png"))
            for img_path in img_files:
                image_tasks.append((student_id, img_path))

        total_images = len(image_tasks)
        if total_images == 0:
            return False, "No image files found inside student dataset folders."

        log_info(f"Starting model training for {total_students} students ({total_images} total images)...")
        start_time = time.time()
        processed_count = 0

        # Primary Engine: face_recognition (128D Encodings)
        if FACE_REC_AVAILABLE:
            engine_type = "face_recognition"
            for student_id, img_path in image_tasks:
                try:
                    image = face_recognition.load_image_file(str(img_path))
                    encodings = face_recognition.face_encodings(image)
                    if len(encodings) > 0:
                        known_encodings.append(encodings[0])
                        known_names.append(student_id)
                except Exception as e:
                    log_error(f"Error processing image {img_path}: {e}")

                processed_count += 1
                elapsed = time.time() - start_time
                avg_time_per_img = elapsed / max(1, processed_count)
                eta = (total_images - processed_count) * avg_time_per_img
                progress_pct = (processed_count / total_images) * 100.0

                if progress_callback:
                    progress_callback(
                        progress_pct,
                        f"Processing {student_id} ({processed_count}/{total_images})",
                        len(known_encodings),
                        eta
                    )

            model_data = {
                "engine": engine_type,
                "encodings": known_encodings,
                "names": known_names,
                "trained_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_faces": len(known_encodings),
                "total_students": len(set(known_names))
            }
        else:
            # Fallback Engine: OpenCV Haar + Gray Face Matrix
            engine_type = "opencv_lbph"
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            face_samples = []
            labels = []
            label_id_counter = 0

            for student_id, img_path in image_tasks:
                if student_id not in student_id_map:
                    student_id_map[student_id] = label_id_counter
                    label_id_counter += 1
                label_id = student_id_map[student_id]

                img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    faces = face_cascade.detectMultiScale(img, 1.1, 4)
                    for (x, y, w, h) in faces:
                        face_samples.append(img[y:y+h, x:x+w])
                        labels.append(label_id)

                processed_count += 1
                elapsed = time.time() - start_time
                avg_time_per_img = elapsed / max(1, processed_count)
                eta = (total_images - processed_count) * avg_time_per_img
                progress_pct = (processed_count / total_images) * 100.0

                if progress_callback:
                    progress_callback(
                        progress_pct,
                        f"Processing {student_id} ({processed_count}/{total_images})",
                        len(face_samples),
                        eta
                    )

            # Train OpenCV LBPH Recognizer
            recognizer = cv2.face.LBPHFaceRecognizer_create() if hasattr(cv2, 'face') else None
            if recognizer and len(face_samples) > 0:
                recognizer.train(face_samples, np.array(labels))
                model_data = {
                    "engine": engine_type,
                    "lbph_model_bytes": recognizer.writeToString(),
                    "id_map": {v: k for k, v in student_id_map.items()},
                    "trained_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "total_faces": len(face_samples),
                    "total_students": len(student_id_map)
                }
            else:
                # Basic backup dictionary model
                model_data = {
                    "engine": "basic_feature_map",
                    "id_map": {v: k for k, v in student_id_map.items()},
                    "trained_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "total_faces": len(face_samples),
                    "total_students": len(student_id_map)
                }

        # Save model file
        os.makedirs(config.TRAINER_DIR, exist_ok=True)
        with open(self.model_path, "wb") as f:
            pickle.dump(model_data, f)

        total_time = round(time.time() - start_time, 2)
        success_msg = f"Training completed successfully in {total_time}s! ({model_data['total_faces']} face encodings saved using {engine_type})."
        log_info(success_msg)
        return True, success_msg
