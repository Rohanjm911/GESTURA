# 🖐️ GESTURA — Neo-Brutalist Adaptive Gesture Studio

**GESTURA** is a touchless human-computer interaction (HCI) desktop studio for Windows that turns any standard webcam into a full multi-monitor mouse and gesture controller. Powered by **MediaPipe Hands**, **OpenCV**, and **CustomTkinter**, it launches straight into a bold **Neo-Brutalist UI** with 6 live-switchable color palettes, custom illustrated hand-pose icons, Per-Monitor DPI-aware multi-monitor tracking, and real-time tuning controls.

---

## 🌟 Key Features

### ⚡ Instant Launch & Neo-Brutalist Studio UI
- **Direct Launch**: Opens immediately into the control studio — no login screen or interruption.
- **Authentic Neo-Brutalist Design**: Thick `#111111` ink borders, hard offset drop shadows, bold high-contrast typography, and matching on-video sticker HUD tags.
- **Custom Illustrated Hand-Pose Icons**: High-DPI anti-aliased hand-pose sticker badges rendered with Pillow (`icons.py`) for every gesture so you can see the exact finger position at a glance.
- **6 Live Color Palettes**: Instant switching via the **`Colors`** quick button or the **`STYLE`** tab swatch grid — updates every card, button, border, shadow, and camera HUD overlay live.

### 🖥️ Multi-Monitor Ready (Per-Monitor DPI Aware)
- **Full Virtual Desktop Support**: Uses Windows Per-Monitor DPI awareness (`EnumDisplayMonitors`) to support dual, triple, mixed-DPI, and **negative-coordinate** (left/top) monitor layouts seamlessly.
- **Flexible Display Targeting**: Switch live between **All Monitors (`ALL 2X` Span)** or lock the tracking box to any individual monitor (`M1`, `M2 ★`, etc.), with a **↻ REFRESH** button for hot-plugged displays.
- **Visual Monitor Dividers & Dead-Zone Clamping**: Displays `M1 | M2` zone markers right inside the camera tracking box when spanning multiple monitors and snaps safely to valid display bounds so the cursor never traps in mismatched monitor corners.

### 🎯 Adaptive Tracking & Full Customization
- **Distance-Adaptive Control + 1-Click Calibration**: Measures apparent palm size in real time to scale the active tracking box and pinch thresholds automatically, plus a **`Calibrate`** button to lock in your current seating distance.
- **3 Organized Control Tabs**:
  - **`CONTROLS`**: Multi-monitor target selector, camera source (`0–3`), resolution presets (`640×480 Fast`, `1280×720 HD`, `1920×1080 FHD`), Right/Left hand dominance, and real-time sliders for **Reach Sensitivity**, **Cursor Smoothing**, **Pinch Tolerance**, and **Scroll Speed**.
  - **`GESTURES`**: Visual illustrated hand-pose guide for core gestures + individual ON/OFF switches for Sniper Mode, Smooth Scrolling, Drag & Drop, Right Click, and Screenshot Capture.
  - **`STYLE`**: 2×3 Neo-Brutalist color palette picker, **Floating Mini-HUD** toggle, Camera Mirroring, optional **Audio Click Cue**, and individual video overlay switches (Hand Skeleton, Active Control Box, On-Video Sticker HUD, Fingertip Tracker Ring).
- **4 Live Telemetry Cards & Mini-HUD**: Displays **Active Gesture**, **FPS & Latency (ms)**, **Active Display**, and **Range % • Session Clicks** — or collapses into a compact always-on-top **Mini-HUD** bar with one-click **EXPAND**.

---

## 🎨 Built-In Neo-Brutalist Color Palettes

| Palette | Mode | Signature Vibe |
| :--- | :---: | :--- |
| **Acid Pop** *(Default)* | Light | Warm Cream Paper + Acid Yellow, Mint, Sky & Pink |
| **Gumroad Pink** | Light | Mint Paper + Hot Pink, Bright Yellow & Electric Teal |
| **Cyber Peach** | Light | Blush Paper + Vivid Tangerine, Acid Lime & Sky Cyan |
| **Blueprint** | Light | Ice Paper + Electric Blue, Signal Yellow & Mint |
| **Vapor Brutal** | Light | Lavender Paper + Vivid Violet, Neon Yellow & Mint |
| **Brutal Dark** | Dark | Pitch Charcoal + Toxic Lime, Cyan, Magenta & Yellow |

---

## 📋 Gesture Reference Guide

| Gesture | Hand Pose | Action | Toggleable |
| :--- | :--- | :--- | :---: |
| **Cursor Navigation** | ☝️ Only Index finger extended | Smooth velocity-adaptive cursor movement | Core (Always On) |
| **Left Click** | ✌️ Index + Middle pinched together | Fires a single left click (debounced per pinch) | Core (Always On) |
| **Double Click** | ✌️ Index + Middle pinched twice (< 400ms) | Fires a clean double click | Core (Always On) |
| **Instant Safe Pause** | 🖐️ Open Palm (all 5 fingers spread) | Freezes cursor movement and safely releases drag | Core (Always On) |
| **Precision Sniper Mode** | 🤘 Index + Pinky extended | Ultra-low sensitivity for pixel-accurate targeting | Yes |
| **Smooth Scrolling** | ✌️ Index + Middle extended & apart (V-sign) | Responsive up/down scrolling matching hand motion | Yes |
| **Drag & Drop** | 👌 Thumb + Index pinched (> 0.3s hold) | Holds left mouse button while moving items | Yes |
| **Right Click** | 🤟 Index + Middle + Ring extended (3 up) | Fires a single right click (non-repeating) | Yes |
| **Screenshot Capture** | ✊ Closed Fist (hold 1.0s) | Launches Windows Snipping Tool (`Win + Shift + S`) | Yes |

---

## 🏗️ Project Architecture

```plaintext
GESTURA/
├── main.py             # Neo-Brutalist CustomTkinter Studio UI, 6 palettes, telemetry, Mini-HUD & camera loop
├── monitor_manager.py  # Per-Monitor DPI aware multi-monitor discovery, negative-coord mapping & dead-zone clamping
├── icons.py            # High-DPI Pillow Neo-Brutalist illustrated hand-pose & UI sticker badge generator
├── gesture_engine.py   # MediaPipe Hands pipeline, debounced gesture state machine & on-video Neo-Brutalist HUD
├── smoother.py         # Dynamic velocity-adaptive exponential cursor smoothing filter
├── run.bat             # One-click Windows launcher
├── requirements.txt    # Pinned Python dependencies
└── README.md           # Project documentation
```

---

## ⚙️ Prerequisites & Setup

### System Requirements
- **OS**: Windows 10 / 11 (64-bit)
- **Python**: Python **3.10.x** *(recommended for official `mediapipe==0.10.14` and `numpy==1.26.4` prebuilt wheels)*
- **Hardware**: Standard USB or built-in webcam (single or multi-monitor setup)

### Virtual Environment Installation
```powershell
# Create Python 3.10 virtual environment
py -3.10 -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

---

## 🚀 How to Run

- **Option 1 (Fastest)**: Double-click **`run.bat`**
- **Option 2 (Terminal)**: Run directly from PowerShell or CMD (`main.py` automatically redirects to `venv\Scripts\python.exe` if invoked from system Python):
  ```powershell
  python main.py
  ```

Click **▶ START GESTURE ENGINE**, hold your hand in front of the webcam, and click **Calibrate** once at your preferred sitting distance for optimal accuracy!

---

## 💡 Tips for Best Accuracy

- **Multi-Monitor Precision**: Use **`ALL (2X)`** when moving windows or browsing across screens, and switch to **`M1`** or **`M2 ★`** when doing detailed editing on a single display.
- **Lighting**: Even front lighting with minimal strong backlight behind your hand keeps MediaPipe tracking locked at peak FPS.
- **Mini-HUD Mode**: Enable **Floating Mini-HUD** in the **`STYLE`** tab when controlling external apps, browsers, or slide decks so the UI stays compact and out of the way.

---

## 🔒 Privacy

All video frames are processed **100% locally in memory** on your machine — no camera feed, landmark data, or images are ever saved to disk or sent over the network.
