# GESTURA

<p align="center">
  <img src="assets/icons/gestura_banner_animated.svg" alt="GESTURA Animated Banner" width="100%" />
</p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.14-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://wiki.qt.io/Qt_for_Python"><img src="https://img.shields.io/badge/PySide6-Qt%206-41CD52?style=for-the-badge&logo=qt&logoColor=white" alt="PySide6"></a>
  <a href="https://opencv.org/"><img src="https://img.shields.io/badge/OpenCV-4.x-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white" alt="OpenCV"></a>
  <a href="https://developers.google.com/mediapipe"><img src="https://img.shields.io/badge/Google_MediaPipe-LiteRT-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Google MediaPipe"></a>
  <a href="https://www.microsoft.com/windows"><img src="https://img.shields.io/badge/Windows-10%20%7C%2011%20(64--bit)-0078D6?style=for-the-badge&logo=windows11&logoColor=white" alt="Windows 11"></a>
  <a href="https://numpy.org/"><img src="https://img.shields.io/badge/NumPy-Scientific-013243?style=for-the-badge&logo=numpy&logoColor=white" alt="NumPy"></a>
  <a href="https://pyinstaller.org/"><img src="https://img.shields.io/badge/PyInstaller-Standalone%20EXE-FFD43B?style=for-the-badge&logo=powershell&logoColor=333" alt="PyInstaller"></a>
</p>

---

## 🌟 1. Project Overview

**GESTURA** is an AI-powered, webcam-based spatial gesture recognition and PC control suite designed specifically for **Windows 10** and **Windows 11**. It transforms any standard HD webcam into an ultra-precise, touch-free input device capable of translating hand movements into low-latency mouse navigation, pinch clicks, drag-and-drop actions, continuous scrolling, keyboard macros, and system-level audio/display adjustments.

With support for both **Single-Hand** and **Dual-Hand Tracking**, GESTURA delivers a fluid, futuristic computing experience wrapped in a modern **Glassmorphism + Cyber-Minimalist** desktop interface.

---

## ⚡ 2. Real-Time Tracking HUD & Telemetry

<p align="center">
  <img src="assets/icons/gestura_hud_animated.svg" alt="GESTURA Real-Time Tracking Animated HUD" width="100%" />
</p>

*Live 21-hand landmark detection powered by Google MediaPipe LiteRT with adaptive One-Euro (1€) jitter filtering and pinch state recognition.*

---

## 🛠️ 3. Technologies & Real-Life Integrations

| Technology | Official Badge | Role in GESTURA |
|---|---|---|
| **Python** | ![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white) | Core application runtime, asynchronous worker threading, and event pipelines. |
| **PySide6 (Qt 6)** | ![Qt](https://img.shields.io/badge/Qt_6_/_PySide6-41CD52?style=flat-square&logo=qt&logoColor=white) | High-performance desktop GUI with hardware-accelerated animations and translucent glass styling. |
| **Google MediaPipe** | ![MediaPipe](https://img.shields.io/badge/Google_MediaPipe-4285F4?style=flat-square&logo=google&logoColor=white) | High-fidelity 21 3D hand landmarks tracking powered by the LiteRT XNNPACK neural engine. |
| **OpenCV** | ![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=flat-square&logo=opencv&logoColor=white) | DirectShow camera video streaming, frame color conversions, and low-latency image ingestion. |
| **Windows APIs** | ![Windows](https://img.shields.io/badge/Windows_API-0078D6?style=flat-square&logo=windows11&logoColor=white) | Native hardware dispatch via `user32.dll` (`SetCursorPos`, `mouse_event`, `keybd_event`) for instant, zero-lag pointer control. |
| **PyCAW & CoreAudio** | ![Audio](https://img.shields.io/badge/Windows_CoreAudio-22D3EE?style=flat-square&logo=windows&logoColor=white) | Master volume decibel scaling and mute state control via modern COM `IAudioEndpointVolume`. |
| **NumPy** | ![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat-square&logo=numpy&logoColor=white) | Vectorized 3D Euclidean distances, angle computations, and One-Euro cursor filtering mathematics. |
| **PyInstaller** | ![PyInstaller](https://img.shields.io/badge/PyInstaller-Standalone%20EXE-FFB900?style=flat-square&logo=cplusplus&logoColor=black) | Compiles and packages all binaries, models, and dependencies into a single zero-install `.exe`. |

---

## 🎯 4. Core Capabilities

### 🖱️ A. Virtual Mouse Controller
- **Index-Finger Pointer Navigation:** Point naturally with your index finger; cursor tracks effortlessly across dual or 4K monitors.
- **Adaptive Cursor Stabilization:** Built with an adaptive **One-Euro (1€) Filter** and Exponential Moving Average (EMA) to completely eliminate hand micro-tremors when stationary while preserving zero-lag response during swift movements.
- **Pinch-to-Click State Machine:**
  - **Thumb + Index Pinch:** Triggers immediate **Left Click** on release.
  - **Double Pinch:** Rapid consecutive pinches execute an OS **Double Click**.
  - **Hold Pinch + Move:** Holding the pinch for over 350ms activates continuous **Drag and Drop** mode until pinch release.
  - **Thumb + Middle Pinch:** Executes a native **Right Click** (context menu).
- **Two-Finger Scrolling:** Extend both index and middle fingers (Peace pose) to smoothly scroll vertically or horizontally with proportional velocity acceleration.
- **Dead-Zone & Margin Normalization:** Edge margins allow reaching all screen corners without touching the physical camera edge.

### 👐 B. Single-Hand & Dual-Hand Tracking
- **Single-Hand Mode:** Fast, hyper-focused interaction loop for primary hand (Left or Right hand selectable).
- **Dual-Hand Mode:** Tracks both hands simultaneously without command collision:
  - **Dual-Hand Zoom:** Expand or contract distance between both hands for dynamic pinch-to-zoom (`Ctrl + Wheel`).
  - **Dual-Hand Volume Slider:** Secondary hand vertical height acts as a master volume slider while the primary hand navigates the cursor.

### 🔊 C. Advanced Windows System Controls
- **Audio Control:** Seamless master volume adjustment, volume increment/decrement, and mute toggle via Windows CoreAudio (pycaw) with native Win32 media key fallback.
- **Display Brightness:** Adjust screen brightness level on internal laptop screens and DDC/CI external monitors.
- **Multimedia Controls:** Play/Pause (Thumb-Up gesture), Next Track, and Previous Track.
- **Keyboard Shortcuts:** Rapid application switching (`Alt + Tab`), Show Desktop (`Win + D`), Task View (`Win + Tab`), and Snipping Tool (`Win + Shift + S`).

### 🛡️ D. Privacy & Safety First
- **100% Offline On-Device Processing:** All computer vision inferencing runs locally via MediaPipe LiteRT. No video frames, telemetry, or images ever leave your computer.
- **Emergency Pause (`ESC`):** Press `ESC` anytime or show an **Open Palm** to immediately suspend tracking.
- **Automatic Button Release:** Any held mouse buttons or drag states are automatically released when tracking stops, the camera is disconnected, or the application exits.

---

## 🎮 5. Gesture Reference Library

| Gesture | Pose Visual | Trigger Description | Default Action |
|---|:---:|---|---|
| **Index Point** | ☝️ | Index extended, others curled | Move Mouse Cursor |
| **Thumb + Index Pinch** | 🤏 | Thumb tip & index tip touching | Left Click / Drag & Drop |
| **Thumb + Middle Pinch** | 🫰 | Thumb tip & middle tip touching | Right Click Context Menu |
| **Two Fingers (Peace)** | ✌️ | Index & middle extended, others curled | Smooth Vertical/Horizontal Scroll |
| **Open Palm** | ✋ | All 5 fingers extended and spread | Emergency Pause Tracking |
| **Closed Fist** | ✊ | All 5 fingers curled | Resume Active Tracking |
| **Thumb Up** | 👍 | Thumb pointed up, others curled | Media Play / Pause |
| **OK Sign** | 👌 | Thumb & index tips circle, others extended | Double Click |
| **Rock On** | 🤘 | Index & pinky extended, middle & ring curled | App Switcher (`Alt + Tab`) |
| **Three Fingers** | 🤟 | Index, middle, and ring extended | Volume Adjustment |
| **Dual-Hand Zoom** | 👐 | Both hands separated, expanding/contracting | Dynamic Zoom In / Zoom Out |
| **Dual-Hand Volume** | 🎚️ | Left hand height slider + Right hand pointer | Continuous System Volume |

---

## ⚡ 6. Running the Application

### Option 1: Standalone Portable Executable (Zero Setup)
Simply double-click the pre-built Windows executable located in the root folder:
```powershell
# Double-click GESTURA.exe in the root project folder:
.\GESTURA.exe
```
> **Note:** Requires no Python installation, no terminal commands, and zero external dependencies.

---

### Option 2: Running from Source Code

#### Prerequisites
- Windows 10 or Windows 11 (64-bit)
- Python 3.10, 3.11, 3.12, or 3.14
- Standard USB or integrated webcam

#### 1. Navigate to Project
```powershell
cd "d:\projects and certificates\projects\personal\GESTURA"
```

#### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

#### 3. Launch GESTURA
```powershell
python main.py
```

---

## 🧪 7. Automated Testing

GESTURA features a complete automated test suite using mocked hardware controllers, ensuring verification runs safely in memory without interfering with your physical mouse cursor or desktop:

```powershell
python -m pytest tests
```
*All 24 automated unit tests pass covering configuration, gesture engines, mouse state machines, smoothing algorithms, and UI views.*

---

## 📦 8. Compiling Standalone Executable

To rebuild the single-file Windows executable:

```powershell
python -m PyInstaller gestura_single.spec --noconfirm
```
The output file will be generated at `dist/GESTURA_Standalone.exe` and copied to `GESTURA.exe`.

---

## 📁 9. Project Architecture

```
GESTURA/
│
├── GESTURA.exe                     # Standalone Windows Executable (Root Launcher)
│
├── app/
│   ├── main.py                     # Main application window & sidebar navigation
│   │
│   ├── core/
│   │   ├── camera.py               # DirectShow webcam capture & FPS engine
│   │   ├── hand_tracking.py        # MediaPipe HandLandmarker & futuristic HUD renderer
│   │   ├── gesture_engine.py       # Geometric finger state & gesture classifier
│   │   ├── gesture_mapper.py       # Temporal validation, cooldowns & action router
│   │   └── tracking_manager.py     # Background QThread worker orchestrator
│   │
│   ├── controllers/
│   │   ├── mouse.py                # Virtual mouse controller (smoothing, pinch, drag)
│   │   ├── keyboard.py             # Windows shortcuts & key simulations
│   │   ├── volume.py               # Windows CoreAudio volume & mute controller
│   │   ├── brightness.py           # Display brightness controller
│   │   └── media.py                # Multimedia key event controller
│   │
│   ├── ui/
│   │   ├── dashboard.py            # Live webcam preview, HUD telemetry & quick controls
│   │   ├── gesture_studio.py       # Custom gesture mapping & live testing playground
│   │   ├── mouse_settings.py       # Pointer physics sliders & interactive sandbox
│   │   ├── system_controls.py      # Direct OS control center
│   │   ├── analytics.py            # Local telemetry metrics & gesture frequency
│   │   ├── settings.py             # Hardware device selection & AI thresholds
│   │   ├── styles.py               # Glassmorphism QSS design system
│   │   └── components/             # Reusable UI components (GlassCard, TelemetryPill, etc.)
│   │
│   ├── services/
│   │   ├── configuration.py        # Thread-safe config service with user overrides
│   │   └── statistics.py           # Usage metrics & lifetime analytics tracker
│   │
│   └── utils/
│       ├── logger.py               # Centralized logging utility
│       ├── smoothing.py            # 1€ Filter & EMA cursor stabilizer
│       └── windows_api.py          # Native Win32 SendInput & mouse_event bindings
│
├── assets/
│   ├── icons/                      # App icon, animated banners & animated HUD SVGs
│   └── models/
│       └── hand_landmarker.task    # Offline MediaPipe hand landmark model
│
├── config/
│   ├── default_config.json         # Default application configuration
│   └── user_config.json            # User-saved overrides
│
├── tests/                          # 24 Automated Unit Tests
├── gestura_single.spec             # PyInstaller Single-File Build Specification
├── gestura.spec                    # PyInstaller Directory Build Specification
├── requirements.txt                # Python package dependencies
├── README.md                       # Documentation
└── main.py                         # Root launcher script
```

---

## 📜 10. License & Credits

Developed with precision by the **GESTURA Team**.  
*Control Beyond Touch.*
