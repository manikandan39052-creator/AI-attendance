"""
FaceAttend AI Pro - Voice Speech Announcement Engine
Threaded text-to-speech engine using pyttsx3.
"""

import threading
import queue
import pyttsx3
import config
from core.logger import log_info, log_error

class VoiceEngine:
    def __init__(self):
        self.speech_queue = queue.Queue()
        self.enabled = config.DEFAULT_VOICE_ENABLED
        self.thread = None
        self.stopped = False

    def start(self):
        """Start background voice worker thread."""
        self.stopped = False
        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()
        return self

    def _worker(self):
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 160)  # Speech speed
            engine.setProperty('volume', 0.9)
        except Exception as e:
            log_error(f"Failed to initialize pyttsx3 engine: {e}")
            engine = None

        while not self.stopped:
            try:
                msg = self.speech_queue.get(timeout=0.5)
                if msg and self.enabled and engine:
                    try:
                        engine.say(msg)
                        engine.runAndWait()
                    except Exception as e:
                        log_error(f"Voice playback error: {e}")
                self.speech_queue.task_done()
            except queue.Empty:
                pass

    def speak(self, text: str):
        """Queue text to be spoken by text-to-speech engine."""
        if self.enabled and text:
            self.speech_queue.put(text)

    def set_enabled(self, enabled: bool):
        self.enabled = enabled

    def stop(self):
        self.stopped = True
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
