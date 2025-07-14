## 🛡️ Real-Time Privacy Overlay using PyQt5 + OpenGL

### 🔍 Overview

This project implements a **real-time, gaze-aware privacy overlay** using Python. It uses **MediaPipe** for facial landmark tracking, **OpenCV** and **MSS** for webcam and screen capture, and **PyQt5 + OpenGL** for a GPU-accelerated fullscreen overlay that **blurs everything on the screen except where the user is looking**.

### 🎯 Key Features

* ✅ **Eye-tracking** using MediaPipe FaceMesh
* ✅ **Fullscreen blur** using OpenCV Gaussian blur
* ✅ **Real-time overlay rendering** using OpenGL textures
* ✅ **Transparent & click-through window**, so you can interact with apps as normal
* ✅ **Flicker/infinite-loop free** screen capture using offscreen window positioning
* ✅ Compatible with **Snapdragon X Elite** or any modern GPU

---

### 🧠 How It Works

1. **Face Tracking**
   A webcam feed is captured using OpenCV, and facial landmarks are detected using MediaPipe's FaceMesh. The 2D coordinates of the left and right eye are used to compute the center of the user's gaze.

2. **Smoothing**
   A moving average filter (with smoothing factor `alpha`) is applied to the gaze position to avoid jitter from small movements.

3. **Screen Capture**
   The full screen is captured using `mss`. To avoid recursive feedback (infinite screen), the overlay window temporarily moves offscreen before the capture and returns immediately afterward.

4. **Blurring**
   The captured screen is blurred using `cv2.GaussianBlur()`. A circular mask is applied around the gaze position to preserve a clear window of visibility.

5. **OpenGL Rendering**
   The processed image (blurred except center) is sent to the GPU as a texture and rendered via `glTexImage2D` onto a fullscreen quad using PyQt5's OpenGL canvas.

6. **Transparent Overlay**
   The PyQt5 window is set to be:

   * Always on top
   * Frameless
   * Transparent to clicks (via Windows API and PyQt5 flags)

---

### 💻 File Structure

```text
privacy_overlay.py     # Main script
```

---

### 📦 Dependencies

Install via pip:

```bash
pip install PyQt5 PyOpenGL opencv-python mss mediapipe numpy pywin32
```

---

### ▶️ How to Run

```bash
python privacy_overlay.py
```

The overlay will launch in fullscreen, blur everything, and automatically track your eyes to reveal a visible area where you're looking.

---

### 🧩 Key Code Components

* `MediaPipe FaceMesh` → Detects face and extracts eye landmarks
* `MSS` → Captures screen without including the overlay itself
* `OpenCV` → Applies blur and circular masking
* `PyOpenGL` → Renders the result efficiently using GPU
* `PyQt5 QGLWidget` → Provides a transparent, fullscreen window
* `win32gui / win32con` → Ensures window does not capture itself

---

### 📌 Notes

* The Gaussian blur kernel is `(45, 45)` by default. Adjust for speed/clarity.
* The visible "unblurred" circular region has radius `130 px`. Change `self.radius` to customize.
* The overlay is **click-through** – you can interact with the underlying desktop normally.

---

