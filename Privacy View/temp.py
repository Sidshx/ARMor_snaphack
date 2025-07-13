from PyQt5 import QtWidgets, QtGui, QtCore, QtOpenGL
from OpenGL.GL import *
import numpy as np
import cv2
import mss
import mediapipe as mp
import ctypes
import sys
import time
import win32gui
import win32con

# === MediaPipe Setup ===
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)

# === Screen Setup ===
sct = mss.mss()
monitor = sct.monitors[1]
screen_width, screen_height = monitor['width'], monitor['height']

# === Smooth Tracking ===
smooth_x, smooth_y = screen_width // 2, screen_height // 2
alpha = 0.2


class GLOverlay(QtOpenGL.QGLWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PrivacyOverlay")
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.WindowTransparentForInput
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setGeometry(0, 0, screen_width, screen_height)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(33)

        self.capture = cv2.VideoCapture(0)
        self.radius = 130
        self.texture_id = None  # Will be initialized in initializeGL

        self.hwnd = None
        QtCore.QTimer.singleShot(1000, self.get_hwnd)  # Delay to ensure window is visible

    def get_hwnd(self):
        def _enum_handler(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                if "PrivacyOverlay" in win32gui.GetWindowText(hwnd):
                    self.hwnd = hwnd
        win32gui.EnumWindows(_enum_handler, None)

    def initializeGL(self):
        self.texture_id = glGenTextures(1)

    def get_blurred_screen(self):
        global smooth_x, smooth_y

        # Hide overlay before capture
        if self.hwnd:
            win32gui.SetWindowPos(self.hwnd, None, -screen_width, -screen_height, 0, 0,
                                  win32con.SWP_NOSIZE | win32con.SWP_NOZORDER)
            time.sleep(0.005)

        img = sct.grab(monitor)

        # Show overlay again
        if self.hwnd:
            win32gui.SetWindowPos(self.hwnd, None, 0, 0, 0, 0,
                                  win32con.SWP_NOSIZE | win32con.SWP_NOZORDER)

        ret, frame = self.capture.read()
        if not ret:
            return np.zeros((screen_height, screen_width, 3), dtype=np.uint8)

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)

        target_x, target_y = screen_width // 2, screen_height // 2
        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark
            left_eye = landmarks[33]
            right_eye = landmarks[263]
            eye_x = (left_eye.x + right_eye.x) / 2
            eye_y = (left_eye.y + right_eye.y) / 2
            target_x = int(eye_x * screen_width)
            target_y = int(eye_y * screen_height)

        smooth_x = int(alpha * target_x + (1 - alpha) * smooth_x)
        smooth_y = int(alpha * target_y + (1 - alpha) * smooth_y)

        img_np = np.array(img)
        img_rgb = cv2.cvtColor(img_np, cv2.COLOR_BGRA2RGB)
        blurred = cv2.GaussianBlur(img_rgb, (45, 45), 0)

        mask = np.zeros((screen_height, screen_width), dtype=np.uint8)
        cv2.circle(mask, (smooth_x, smooth_y), self.radius, 255, -1)
        mask_3ch = np.stack([mask] * 3, axis=-1)
        result = np.where(mask_3ch == 255, img_rgb, blurred)

        return result

    def paintGL(self):
        if self.texture_id is None:
            return

        frame = self.get_blurred_screen()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, screen_width, screen_height, 0, GL_RGB, GL_UNSIGNED_BYTE, frame.tobytes())
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(-1, 1)
        glTexCoord2f(1, 0); glVertex2f(1, 1)
        glTexCoord2f(1, 1); glVertex2f(1, -1)
        glTexCoord2f(0, 1); glVertex2f(-1, -1)
        glEnd()

        glDisable(GL_TEXTURE_2D)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    overlay = GLOverlay()
    overlay.showFullScreen()

    # Ensure it's always-on-top and click-through
    ctypes.windll.user32.SetWindowPos(int(overlay.winId()), -1, 0, 0, 0, 0, 0x0001 | 0x0002)
    sys.exit(app.exec_())
