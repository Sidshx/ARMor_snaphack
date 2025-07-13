import cv2
import numpy as np
import mss
import time
import mediapipe as mp
import tkinter as tk
import win32gui
import win32con
import win32api
from PIL import Image, ImageTk

# === MediaPipe Setup ===
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)

# === Screen Setup ===
sct = mss.mss()
monitor = sct.monitors[1]
screen_width, screen_height = monitor['width'], monitor['height']

# === Tkinter Transparent Fullscreen Window ===
root = tk.Tk()
root.title("Privacy Overlay")
root.geometry(f"{screen_width}x{screen_height}+0+0")
root.configure(bg='white')
root.attributes('-transparentcolor', 'white')
root.attributes('-topmost', True)
root.overrideredirect(True)

label = tk.Label(root, bg='white')
label.pack(fill='both', expand=True)

# === Click-Through Window ===
def make_window_click_through(window_title="Privacy Overlay", retries=10, delay=0.2):
    for _ in range(retries):
        hwnd = win32gui.FindWindow(None, window_title)
        if hwnd:
            exStyle = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                                   exStyle | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)
            win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(255, 255, 255), 0, win32con.LWA_COLORKEY)
            return hwnd
        time.sleep(delay)
    raise RuntimeError(f"Window '{window_title}' not found.")

root.update()
hwnd = make_window_click_through("Privacy Overlay")

# === Webcam ===
cap = cv2.VideoCapture(0)
photo_img = None

# === Smoothing ===
smooth_cx, smooth_cy = screen_width // 2, screen_height // 2
alpha = 0.2  # Smoothing factor

def capture_screen_without_overlay():
    # Temporarily move window off-screen instead of hiding
    win32gui.SetWindowPos(hwnd, None, -screen_width, -screen_height, 0, 0, win32con.SWP_NOSIZE | win32con.SWP_NOZORDER)
    time.sleep(0.005)  # small delay to avoid flicker
    img = sct.grab(monitor)
    img_np = np.array(img)
    # Move window back instantly
    win32gui.SetWindowPos(hwnd, None, 0, 0, 0, 0, win32con.SWP_NOSIZE | win32con.SWP_NOZORDER)
    return cv2.cvtColor(img_np, cv2.COLOR_BGRA2RGB)

def fast_blur_except_circle(img, cx, cy, radius=130):
    blurred = cv2.GaussianBlur(img, (45, 45), 0)
    mask = np.zeros((screen_height, screen_width), dtype=np.uint8)
    cv2.circle(mask, (cx, cy), radius, 255, -1)
    mask_3ch = np.stack([mask]*3, axis=-1)
    return np.where(mask_3ch == 255, img, blurred)

def update():
    global photo_img, smooth_cx, smooth_cy

    ret, frame = cap.read()
    if not ret:
        root.after(33, update)
        return

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    target_cx, target_cy = screen_width // 2, screen_height // 2

    if results.multi_face_landmarks:
        landmarks = results.multi_face_landmarks[0].landmark
        left_eye = landmarks[33]
        right_eye = landmarks[263]
        eye_x = (left_eye.x + right_eye.x) / 2
        eye_y = (left_eye.y + right_eye.y) / 2
        target_cx = int(eye_x * screen_width)
        target_cy = int(eye_y * screen_height)

    # Smooth
    # smooth_cx = int(alpha * target_cx + (1 - alpha) * smooth_cx)
    # smooth_cy = int(alpha * target_cy + (1 - alpha) * smooth_cy)

    smooth_cx = target_cx
    smooth_cy = target_cy

    screen_np = capture_screen_without_overlay()
    processed_np = fast_blur_except_circle(screen_np, smooth_cx, smooth_cy)

    final_img = Image.fromarray(processed_np)
    photo_img = ImageTk.PhotoImage(final_img)
    label.configure(image=photo_img)

    root.after(100, update)

update()
root.mainloop()
cap.release()
