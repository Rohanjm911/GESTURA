# GESTURA
### Control Beyond Touch.
**Ultimate Gesture-Controlled Windows Desktop Application**

---

## 🌟 1. Project Overview

**GESTURA** is an AI-powered, webcam-based gesture recognition and PC control application designed for Windows 10 and Windows 11. It transforms any standard webcam into an intelligent, high-precision spatial input device capable of recognizing hand movements and translating them into fluid mouse navigation, clicks, drag-and-drop operations, keyboard shortcuts, and OS-level system controls.

Supporting both **single-hand** and **dual-hand tracking**, GESTURA offers an ultra-responsive, touch-free PC interaction experience wrapped in a modern **Glassmorphism + Futuristic Minimalism** desktop interface.

---

## 🎯 2. Core Capabilities

### A. Virtual Mouse Controller
- **Index-Finger Cursor Navigation:** Point with your index finger for natural pointer control.
- **Adaptive Cursor Stabilization:** Employs an adaptive **One-Euro (1€) Filter** and Exponential Moving Average (EMA) with micro-tremor dead-zone filtering to eliminate jitter when stationary while preserving zero-lag response during swift movements.
- **Pinch-to-Click:**
  - **Thumb + Index Pinch:** Triggers immediate Left Click upon release.
  - **Double Pinch:** Rapid double pinch executes a Double Click.
  - **Hold Pinch + Move:** Holding the pinch past the configurable threshold activates **Drag and Drop** mode until pinch release.
  - **Thumb + Middle Pinch:** Executes Right Click context menu invocation.
- **Two-Finger Scrolling:** Extend index and middle fingers in a "Peace" gesture to scroll vertically or horizontally with proportional velocity acceleration.
- **Edge Reach Margins:** Configurable interaction box allows reaching all screen corners without extending hand to extreme webcam boundaries.

### B. One-Hand & Dual-Hand Tracking
- **Single-Hand Mode:** Fast, focused interaction mapping for primary hand (configurable Left or Right).
- **Dual-Hand Mode:** Tracks both hands simultaneously:
  - **Dual-Hand Zoom:** Expand or contract distance between hands for pinch-to-zoom (Ctrl + Wheel).
  - **Dual-Hand Volume Slider:** Use the secondary hand's height as a continuous master volume slider while navigating with the primary hand.
  - Independent, conflict-free multi-hand command arbitration.

### C. Advanced System & OS Controls
- **Audio Control:** Seamless master volume adjustment, volume increment/decrement, and mute toggle via Windows CoreAudio (pycaw) with native Win32 media key fallback.
- **Display Brightness:** Adjust screen brightness level on internal and DDC/CI external displays.
- **Multimedia Playback:** Windows-native Play/Pause (Thumb-Up gesture), Next Track, and Previous Track.
- **Window Management:** Instant application switching (`Alt + Tab`), Show Desktop (`Win + D`), Task View (`Win + Tab`), and Snipping Tool (`Win + Shift + S`).

### D. Safety & Privacy Safeguards
- **100% Local On-Device AI:** Operates entirely offline using Google MediaPipe LiteRT XNNPACK delegate. No images or videos are ever saved, recorded, or transmitted to any external server.
- **Instant Emergency Pause:**
  - Global Hotkey: Press **`ESC`** anytime to immediately disable gesture input.
  - Hand Gesture: Flash an **`Open Palm`** to pause tracking.
  - Resume: Form a **`Closed Fist`** to safely re-enable tracking.
- **Automatic Button Lock Release:** Any held mouse buttons or drag states are automatically and safely released when tracking pauses, camera disconnects, or the application closes.

---

## 🏗️ 3. Technology Stack

| Component | Technology | Purpose |
|---|---|---|
| **Language** | Python 3.10+ / 3.13 / 3.14 | Core application logic and async threading |
| **GUI Framework** | PySide6 (Qt for Python) | Desktop UI with custom Glassmorphism styles |
| **Computer Vision** | OpenCV (`cv2`) | DirectShow low-latency webcam capture |
| **Hand Landmark AI** | Google MediaPipe 1.2+ / LiteRT | 21 3D hand landmarks tracking |
| **Mouse & Keyboard** | Windows Win32 API & PyAutoGUI | Direct zero-latency hardware input simulation |
| **Audio & Brightness** | `pycaw`, `screen-brightness-control` | Windows CoreAudio endpoints & WMI brightness |
| **Config & Stats** | JSON | Local persistent configuration and analytics |
| **Distribution** | PyInstaller | Standalone Windows distributable executable |

---

## 📁 4. Application Architecture

```
GESTURA/
│
├── app/
│   ├── main.py                     # Main window, sidebar, and application entry point
│   │
│   ├── core/
│   │   ├── camera.py               # DirectShow webcam capture & FPS engine
│   │   ├── hand_tracking.py        # MediaPipe HandLandmarker & futuristic HUD renderer
│   │   ├── gesture_engine.py       # Geometric finger state & gesture classifier
│   │   ├── gesture_mapper.py       # Temporal validation, cooldowns, & action router
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
│   │   └── components/
│   │       ├── glass_card.py       # Frosted glass card container
│   │       ├── telemetry_pill.py   # Status indicator badges
│   │       └── toggle_switch.py    # Animated toggle switch widget
│   │
│   ├── services/
│   │   ├── configuration.py        # Thread-safe config service with user overrides
│   │   └── statistics.py           # Usage metrics & lifetime analytics tracker
│   │
│   └── utils/
│       ├── logger.py               # Structured application logger
│       ├── smoothing.py            # 1€ (One-Euro) Filter & EMA cursor stabilizer
│       └── windows_api.py          # Native Win32 SendInput & mouse_event bindings
│
├── assets/
│   ├── icons/                      # App icon (.ico and .png)
│   └── models/
│       └── hand_landmarker.task    # Offline MediaPipe hand landmark model
│
├── config/
│   ├── default_config.json         # Default application configuration
│   └── user_config.json            # User-saved overrides (generated at runtime)
│
├── tests/
│   ├── test_config.py              # Configuration service unit tests
│   ├── test_gesture_engine.py      # Gesture classifier unit tests
│   ├── test_gesture_mapper.py      # Action routing & temporal validation tests
│   ├── test_mouse_controller.py    # Virtual mouse & smoothing unit tests
│   ├── test_system_controllers.py  # Audio, brightness, and keyboard tests
│   ├── test_tracking_manager.py    # Background worker lifecycle tests
│   └── test_ui.py                  # PySide6 GUI views & navigation tests
│
├── gestura.spec                    # PyInstaller build specification
├── requirements.txt                # Python package dependencies
├── README.md                       # Comprehensive documentation
└── main.py                         # Root launcher script
```

---

## 🚀 5. Installation & Setup

### Prerequisites
- Windows 10 or Windows 11 (64-bit)
- Python 3.10 or higher
- A standard USB or built-in webcam

### Step 1: Clone or Navigate to the Repository
```powershell
cd "d:\projects and certificates\projects\personal\GESTURA"
```

### Step 2: Install Required Dependencies
```powershell
pip install -r requirements.txt
```

### Step 3: Run the Application
```powershell
python main.py
```

---

## 🧪 6. Running Automated Tests

GESTURA includes a comprehensive automated test suite with mocked hardware controllers so tests run safely in memory without moving the real mouse cursor or altering system volume:

```powershell
python -m pytest tests
```

---

## 📦 7. Building Standalone Windows Executable

To generate a distributable Windows executable (`GESTURA.exe`) with PyInstaller:

```powershell
python -m PyInstaller gestura.spec --noconfirm
```

The output standalone folder will be generated in:
```
dist/GESTURA/
```
Inside `dist/GESTURA/`, double-click `GESTURA.exe` to run the application with zero Python environment requirements.

---

## 🎮 8. Gesture Control Reference

| Gesture | Pose Description | Default Action | Configurable |
|---|---|---|---|
| **Index Point** | Index finger extended, others curled | Move Mouse Cursor | Yes |
| **Thumb + Index Pinch** | Pinch thumb tip and index fingertip together | Left Click (Quick) / Drag & Drop (Hold) | Yes |
| **Thumb + Middle Pinch** | Pinch thumb tip and middle fingertip together | Right Click Context Menu | Yes |
| **Two Fingers (Peace)** | Index and middle fingers extended | Smooth Scroll (Vertical & Horizontal) | Yes |
| **Open Palm** | All 5 fingers extended and spread | Emergency Pause Tracking | Yes |
| **Closed Fist** | All 5 fingers curled into a ball | Resume Tracking | Yes |
| **Thumb Up** | Thumb pointed up, other fingers curled | Media Play / Pause | Yes |
| **OK Sign** | Thumb and index tips touching, 3 fingers extended | Double Click | Yes |
| **Rock On** | Index and pinky extended, middle and ring curled | Switch Active App (`Alt + Tab`) | Yes |
| **Three Fingers** | Index, middle, and ring extended | Volume Adjustment Slider | Yes |
| **Dual-Hand Zoom** | Both hands present, adjusting distance | Pinch to Zoom (`Ctrl + Wheel`) | Yes |
| **Dual-Hand Volume** | Left hand height slider + Right hand cursor | Proportional Master Volume Slider | Yes |

---

## 🛡️ 9. Privacy & Security Architecture

1. **Zero Cloud Latency & Zero Transmission:** All computer vision inferencing occurs locally in memory using the on-device `hand_landmarker.task` LiteRT neural network.
2. **No Video Recording:** Webcam frames are read directly from RAM buffer, processed, rendered to the viewport, and discarded immediately. No video or images are written to disk.
3. **Fail-Safe Mechanism:** Releasing the pinch releases mouse locks; pausing or stopping tracking immediately calls `release_all_mouse_buttons()`.

---

## 📜 10. License & Credits

Developed with precision by the **GESTURA Team**.
*Control Beyond Touch.*
