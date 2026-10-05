"""
FaceAttend AI Pro - Threaded Camera Feed
Non-blocking OpenCV camera wrapper for high-performance UI rendering.
"""

import cv2
import threading
import time
from core.logger import log_info, log_error

class CameraStream:
    def __init__(self, src: int = 0, width: int = 640, height: int = 480):
        self.src = src
        self.width = width
        self.height = height

        self.cap = cv2.VideoCapture(self.src, cv2.CAP_DSHOW) if cv2.os.name == 'nt' else cv2.VideoCapture(self.src)
        if self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        self.grabbed, self.frame = self.cap.read()
        self.stopped = False
        self.thread = None

        # FPS calculation
        self.prev_time = time.time()
        self.fps = 0.0

    def start(self):
        """Start the video stream thread."""
        if not self.cap.isOpened():
            log_error(f"Cannot open camera index {self.src}")
            return self

        self.stopped = False
        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()
        log_info(f"Camera stream started on index {self.src}")
        return self

    def _update(self):
        while not self.stopped:
            if not self.cap.isOpened():
                break

            grabbed, frame = self.cap.read()
            if grabbed:
                curr_time = time.time()
                self.fps = 1.0 / max(0.001, (curr_time - self.prev_time))
                self.prev_time = curr_time
                self.frame = frame
                self.grabbed = grabbed
            else:
                time.sleep(0.01)

    def read(self):
        """Return the current frame and FPS."""
        return self.grabbed, self.frame, self.fps

    def stop(self):
        """Stop the camera stream thread and release resources."""
        self.stopped = True
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        if self.cap and self.cap.isOpened():
            self.cap.release()
        log_info("Camera stream released.")

    def is_opened(self) -> bool:
        return self.cap.isOpened()
