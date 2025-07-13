## 🛡 ARMOR: Privacy and Troubleshooting for Windows-on-ARM

### 🔍 Overview

**ARMOR** is a dual-function project designed for Windows-on-ARM systems, such as those running on Snapdragon X Elite laptops. It combines two powerful utilities:

1. **Real-Time Privacy Overlay**: A gaze-aware privacy overlay that uses eye-tracking to blur the screen except where the user is looking, ensuring privacy in shared environments.
2. **Troubleshooting Assistant**: A local assistant agent that leverages Windows event logs and a locally hosted large language model (LLM) to diagnose and resolve system issues.

Both functions run locally, prioritizing privacy and performance on ARM-based Windows devices.

### 🎯 Key Features

#### Privacy Overlay
* ✅ **Eye-tracking** using MediaPipe FaceMesh for gaze detection.
* ✅ **Fullscreen blur** with a clear window around the user’s gaze using OpenCV Gaussian blur.
* ✅ **Real-time rendering** with PyQt5 and OpenGL for GPU-accelerated overlays.
* ✅ **Transparent & click-through window**, allowing normal interaction with underlying applications.
* ✅ **Flicker-free screen capture** by temporarily moving the overlay offscreen.
* ✅ Optimized for **Snapdragon X Elite** and other modern GPUs.

#### Troubleshooting Assistant
* ✅ **System Log Extraction**: Retrieves recent Windows event logs (System, Application, Security) using `pywin32`.
* ✅ **Local LLM Integration**: Queries a locally hosted LLM (e.g., via VSCode AI Toolkit) for intelligent troubleshooting.
* ✅ **ARM-Specific Troubleshooting**: Tailored for diagnosing issues on Windows-on-ARM devices.
* ✅ **Privacy-First**: Runs entirely locally, ensuring no data leaves the device.

---

### 🧠 How It Works

#### 1. Privacy Overlay
- **Face Tracking**: Captures webcam feed via OpenCV and uses MediaPipe FaceMesh to detect facial landmarks, calculating the gaze center from eye coordinates.
- **Smoothing**: Applies a moving average filter (with smoothing factor `alpha`) to stabilize gaze position and reduce jitter.
- **Screen Capture**: Uses `mss` to capture the full screen, temporarily moving the overlay offscreen to avoid recursive feedback.
- **Blurring**: Applies `cv2.GaussianBlur()` to the screen, preserving a clear circular region around the gaze.
- **OpenGL Rendering**: Renders the processed image (blurred except gaze area) as a GPU texture via `glTexImage2D` on a PyQt5 OpenGL canvas.
- **Transparent Overlay**: Configures the PyQt5 window to be always on top, frameless, and click-through using Windows API and PyQt5 flags.

#### 2. Troubleshooting Assistant
- **Log Extraction**: Uses `pywin32` to extract recent Windows event logs (e.g., System logs) with details like timestamp, event type (ERROR, WARNING, INFO), and message.
- **LLM Query**: Sends the user’s question and relevant logs to a locally hosted LLM (e.g., `qnn-deepseek-r1-distill-qwen-1.5b`) via an OpenAI-compatible API for diagnosis and solutions.
- **Response Delivery**: Returns clear, actionable troubleshooting steps in English, referencing only relevant log entries.

---

### 💻 File Structure

```text
ARMbot/armbot.py              # Script for the troubleshooting assistant
Privacy View/privacy_overlay.py  # Script for the real-time privacy overlay
```

---

### 📦 Dependencies

Install via pip:

```bash
pip install PyQt5 PyOpenGL opencv-python mss mediapipe numpy pywin32 openai
```

For the troubleshooting assistant, set up a local LLM server using the **VSCode AI Toolkit**. Follow the setup tutorial: [VSCode AI Toolkit Getting Started](https://learn.microsoft.com/en-us/windows/ai/toolkit/toolkit-getting-started?tabs=rest).

---

### ▶ How to Run

#### Privacy Overlay
1. Install dependencies (see above).
2. Run the overlay script:

```bash
python "Privacy View/privacy_overlay.py"
```

The overlay launches in fullscreen, blurs the screen, and tracks your eyes to reveal a clear area where you’re looking.

#### Troubleshooting Assistant
1. Ensure a local LLM server is running at `http://localhost:5272/v1`, or modify the `client` to match the localhost address.
2. Install dependencies (see above).
3. Run the assistant script:

```bash
python ARMbot/armbot.py
```

4. Enter your troubleshooting question (e.g., "Why is my Snapdragon X Elite laptop crashing?") when prompted.

---

### 🧩 Key Code Components

#### Privacy Overlay
* `MediaPipe FaceMesh` → Detects face and extracts eye landmarks.
* `MSS` → Captures screen without including the overlay.
* `OpenCV` → Applies Gaussian blur and circular masking.
* `PyOpenGL` → Renders the result efficiently using GPU.
* `PyQt5 QGLWidget` → Provides a transparent, fullscreen window.
* `win32gui / win32con` → Ensures the window does not capture itself.

#### Troubleshooting Assistant
* `pywin32` → Extracts Windows event logs using `win32evtlog` and `win32evtlogutil`.
* `openai` → Communicates with the local LLM server via an OpenAI-compatible API.
* `datetime` → Processes log timestamps for readability.

---

### 📌 Notes

#### Privacy Overlay
* The Gaussian blur kernel is `(45, 45)` by default. Adjust for speed or clarity.
* The unblurred circular region has a radius of `130 px`. Modify `self.radius` to customize.
* The overlay is **click-through**, allowing normal interaction with the desktop.

#### Troubleshooting Assistant
* Defaults to extracting the 15 most recent System logs. Adjust `max_entries` in `extract_windows_logs` to change this.
* Supports only System, Application, and Security logs. Modify `valid` in `extract_windows_logs` to extend support.
* The LLM model (`qnn-deepseek-r1-distill-qwen-1.5b`) is an example. Other localhost-compatible models can be used by updating the `model` parameter in `query_llm` and `client`.
* Ensure the local LLM server is running before executing `armbot.py`.

---