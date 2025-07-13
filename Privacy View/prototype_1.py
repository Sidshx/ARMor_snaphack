import cv2
import numpy as np
import mss
from PIL import Image, ImageDraw, ImageFilter
import mediapipe as mp

# Init camera and face mesh
cap = cv2.VideoCapture(0)
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)

# Define safe screen region (top-left 800x600)
monitor = {"top": 0, "left": 0, "width": 800, "height": 600}
screen_width, screen_height = monitor["width"], monitor["height"]

sct = mss.mss()

def get_screen_image():
    screen = sct.grab(monitor)
    return Image.frombytes("RGB", screen.size, screen.rgb)

def blur_except_focus(img, fx, fy, radius=100):
    blurred = img.filter(ImageFilter.GaussianBlur(15))
    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((fx - radius, fy - radius, fx + radius, fy + radius), fill=255)
    return Image.composite(img, blurred, mask)

print("[INFO] Press 'q' to quit.")
while True:
    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.flip(frame, 1)
    h, w = frame.shape[:2]
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    gaze_x, gaze_y = screen_width // 2, screen_height // 2

    if results.multi_face_landmarks:
        lm = results.multi_face_landmarks[0].landmark
        left_eye = lm[33]
        right_eye = lm[263]
        gaze_x = int((left_eye.x + right_eye.x) / 2 * screen_width)
        gaze_y = int((left_eye.y + right_eye.y) / 2 * screen_height)

    screen_img = get_screen_image()
    result = blur_except_focus(screen_img, gaze_x, gaze_y)

    result_np = np.array(result)
    result_np = cv2.cvtColor(result_np, cv2.COLOR_RGB2BGR)
    cv2.imshow("Gaze Privacy Blur (Safe Zone)", result_np)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
