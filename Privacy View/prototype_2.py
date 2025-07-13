import cv2
import numpy as np
import mss
import time
from PIL import Image, ImageDraw, ImageFilter, ImageTk
import mediapipe as mp
import tkinter as tk
import win32gui
import win32con
import win32api

# MediaPipe setup
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)

# Screen grab setup
sct = mss.mss()
monitor = sct.monitors[1]  # Adjust this if you have multiple monitors
screen_width, screen_height = monitor['width'], monitor['height']

# Tkinter GUI setup
root = tk.Tk()
root.title("PrivacyOverlay")
root.geometry(f"{screen_width}x{screen_height}+0+0")
root.configure(bg='white')
root.attributes('-transparentcolor', 'white')
root.attributes('-topmost', True)

canvas = tk.Canvas(root, width=screen_width, height=screen_height, bg='white', highlightthickness=0)
canvas.pack()

root.update_idletasks()
time.sleep(0.5)

# Click-through window setup
hwnd = win32gui.FindWindow(None, "PrivacyOverlay")
if hwnd:
    exStyle = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, exStyle | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)
    win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(255, 255, 255), 0, win32con.LWA_COLORKEY)
else:
    print("[ERROR] Could not find window handle.")

# Webcam setup
cap = cv2.VideoCapture(0)
photo_img = None

def get_screen_image():
    if hwnd:
        # Move the overlay window offscreen
        win32gui.SetWindowPos(hwnd, None, -screen_width, -screen_height, 0, 0,
                              win32con.SWP_NOSIZE | win32con.SWP_NOZORDER)

    img = sct.grab(monitor)

    if hwnd:
        # Move the overlay window back to (0, 0)
        win32gui.SetWindowPos(hwnd, None, 0, 0, 0, 0,
                              win32con.SWP_NOSIZE | win32con.SWP_NOZORDER)

    return Image.frombytes('RGB', img.size, img.rgb)

def blur_except_circle(image, cx, cy, radius=150):
    blurred = image.filter(ImageFilter.GaussianBlur(15))
    mask = Image.new('L', image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=255)
    return Image.composite(image, blurred, mask)

def update():
    global photo_img

    ret, frame = cap.read()
    if not ret:
        root.after(10, update)
        return

    frame = cv2.flip(frame, 1)
    h, w = frame.shape[:2]
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    cx, cy = screen_width // 2, screen_height // 2

    if results.multi_face_landmarks:
        landmarks = results.multi_face_landmarks[0].landmark
        left_eye = landmarks[33]
        right_eye = landmarks[263]
        eye_x = (left_eye.x + right_eye.x) / 2
        eye_y = (left_eye.y + right_eye.y) / 2
        cx = int(eye_x * screen_width)
        cy = int(eye_y * screen_height)

    screen_img = get_screen_image()
    final_img = blur_except_circle(screen_img, cx, cy, radius=130)

    photo_img = ImageTk.PhotoImage(final_img)
    canvas.delete("all")
    canvas.create_image(0, 0, anchor='nw', image=photo_img)

    root.after(5, update)

update()
root.mainloop()
cap.release()
