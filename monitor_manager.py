import ctypes
import ctypes.wintypes
from dataclasses import dataclass


class _RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long),
    ]


class _MONITORINFOEX(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.wintypes.DWORD),
        ("rcMonitor", _RECT),
        ("rcWork", _RECT),
        ("dwFlags", ctypes.wintypes.DWORD),
        ("szDevice", ctypes.wintypes.WCHAR * 32),
    ]


@dataclass
class MonitorInfo:
    index: int          # 1-based display index sorted left-to-right
    device: str
    is_primary: bool
    left: int
    top: int
    right: int
    bottom: int

    @property
    def width(self) -> int:
        return self.right - self.left

    @property
    def height(self) -> int:
        return self.bottom - self.top

    @property
    def label(self) -> str:
        tag = " ★ Primary" if self.is_primary else ""
        return f"Monitor {self.index} ({self.width}x{self.height}){tag}"

    @property
    def short_label(self) -> str:
        return f"Monitor {self.index}" + (" ★" if self.is_primary else "")

    def contains(self, x: int, y: int) -> bool:
        return self.left <= x < self.right and self.top <= y < self.bottom

    def clamp_point(self, x: int, y: int) -> tuple[int, int]:
        cx = max(self.left, min(self.right - 1, x))
        cy = max(self.top, min(self.bottom - 1, y))
        return cx, cy


def enable_per_monitor_dpi_awareness():
    """Ensure Windows reports true physical pixel coordinates across mixed-DPI multi-monitors."""
    try:
        # Windows 10 1703+ Per-Monitor v2 (-4 = DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2)
        ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
        return
    except Exception:
        pass
    try:
        # Windows 8.1+ Per-Monitor DPI Aware (2)
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
        return
    except Exception:
        pass
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


class MonitorManager:
    """Detects and manages single & multi-monitor virtual desktop bounds on Windows."""

    ALL_KEY = "ALL"

    def __init__(self):
        enable_per_monitor_dpi_awareness()
        self.monitors: list[MonitorInfo] = []
        self.virtual_bounds: tuple[int, int, int, int] = (0, 0, 1920, 1080)  # left, top, right, bottom
        self.target_mode: str = self.ALL_KEY  # "ALL" or monitor index string ("1", "2", ...)
        self.refresh()

    def refresh(self) -> list[MonitorInfo]:
        raw_monitors = []
        try:
            user32 = ctypes.windll.user32

            def _cb(hMonitor, hdcMonitor, lprcMonitor, dwData):
                mi = _MONITORINFOEX()
                mi.cbSize = ctypes.sizeof(_MONITORINFOEX)
                if user32.GetMonitorInfoW(hMonitor, ctypes.byref(mi)):
                    r = mi.rcMonitor
                    raw_monitors.append({
                        "device": mi.szDevice,
                        "is_primary": bool(mi.dwFlags & 1),
                        "left": int(r.left),
                        "top": int(r.top),
                        "right": int(r.right),
                        "bottom": int(r.bottom),
                    })
                return 1

            MONITORENUMPROC = ctypes.WINFUNCTYPE(
                ctypes.c_int,
                ctypes.c_void_p,
                ctypes.c_void_p,
                ctypes.POINTER(_RECT),
                ctypes.c_double,
            )
            user32.EnumDisplayMonitors(0, 0, MONITORENUMPROC(_cb), 0)
        except Exception:
            pass

        if not raw_monitors:
            try:
                user32 = ctypes.windll.user32
                w = user32.GetSystemMetrics(0) or 1920
                h = user32.GetSystemMetrics(1) or 1080
            except Exception:
                w, h = 1920, 1080
            raw_monitors.append({
                "device": "PRIMARY",
                "is_primary": True,
                "left": 0, "top": 0, "right": w, "bottom": h,
            })

        # Sort naturally left-to-right, then top-to-bottom
        raw_monitors.sort(key=lambda m: (m["left"], m["top"]))

        self.monitors = [
            MonitorInfo(
                index=i + 1,
                device=m["device"],
                is_primary=m["is_primary"],
                left=m["left"],
                top=m["top"],
                right=m["right"],
                bottom=m["bottom"],
            )
            for i, m in enumerate(raw_monitors)
        ]

        v_left = min(m.left for m in self.monitors)
        v_top = min(m.top for m in self.monitors)
        v_right = max(m.right for m in self.monitors)
        v_bottom = max(m.bottom for m in self.monitors)
        self.virtual_bounds = (v_left, v_top, v_right, v_bottom)

        # Keep target_mode valid if a monitor was unplugged
        if self.target_mode != self.ALL_KEY:
            valid_ids = {str(m.index) for m in self.monitors}
            if self.target_mode not in valid_ids:
                self.target_mode = self.ALL_KEY

        return self.monitors

    @property
    def is_spanning_multiple(self) -> bool:
        return self.target_mode == self.ALL_KEY and len(self.monitors) > 1

    def get_target_bounds(self) -> tuple[int, int, int, int]:
        """Returns (left, top, right, bottom) for the active target monitor or full virtual desktop."""
        if self.target_mode == self.ALL_KEY or len(self.monitors) == 1:
            return self.virtual_bounds
        for m in self.monitors:
            if str(m.index) == self.target_mode:
                return (m.left, m.top, m.right, m.bottom)
        return self.virtual_bounds

    def get_target_label(self) -> str:
        if self.target_mode == self.ALL_KEY:
            if len(self.monitors) > 1:
                vw = self.virtual_bounds[2] - self.virtual_bounds[0]
                vh = self.virtual_bounds[3] - self.virtual_bounds[1]
                return f"All Monitors ({len(self.monitors)}x • {vw}x{vh})"
            return self.monitors[0].label
        for m in self.monitors:
            if str(m.index) == self.target_mode:
                return m.label
        return self.monitors[0].label

    def get_dropdown_options(self) -> list[tuple[str, str]]:
        """Returns list of (mode_key, display_label) for UI selection."""
        opts = []
        if len(self.monitors) > 1:
            vw = self.virtual_bounds[2] - self.virtual_bounds[0]
            vh = self.virtual_bounds[3] - self.virtual_bounds[1]
            opts.append((self.ALL_KEY, f"All Monitors • Span ({vw}x{vh})"))
        for m in self.monitors:
            opts.append((str(m.index), m.label))
        return opts

    def set_target(self, mode_key: str):
        self.target_mode = mode_key

    def clamp_to_valid_screen(self, x: int, y: int) -> tuple[int, int]:
        """
        Clamps (x, y) to the selected monitor, or if spanning multiple monitors of mismatched
        sizes/offsets, snaps cleanly to the nearest real monitor so the cursor never hits dead zones.
        """
        if self.target_mode != self.ALL_KEY:
            for m in self.monitors:
                if str(m.index) == self.target_mode:
                    return m.clamp_point(x, y)

        # In ALL mode, check if point is already inside a real monitor
        for m in self.monitors:
            if m.contains(x, y):
                return x, y

        # Otherwise snap to nearest valid point across all monitors
        best_pt = self.monitors[0].clamp_point(x, y)
        best_dist = (best_pt[0] - x) ** 2 + (best_pt[1] - y) ** 2
        for m in self.monitors[1:]:
            pt = m.clamp_point(x, y)
            dist = (pt[0] - x) ** 2 + (pt[1] - y) ** 2
            if dist < best_dist:
                best_dist = dist
                best_pt = pt
        return best_pt

    def get_monitor_at(self, x: int, y: int) -> MonitorInfo:
        for m in self.monitors:
            if m.contains(x, y):
                return m
        return self.monitors[0]

    def get_normalized_dividers(self) -> list[float]:
        """
        Returns normalized X positions (0.0 .. 1.0) of monitor boundaries within the virtual desktop
        so the camera active box can render visual screen dividers when spanning multiple monitors.
        """
        if not self.is_spanning_multiple:
            return []
        v_left, _, v_right, _ = self.virtual_bounds
        v_width = max(v_right - v_left, 1)
        dividers = []
        for m in self.monitors:
            if v_left < m.left < v_right:
                dividers.append((m.left - v_left) / v_width)
        return sorted(set(dividers))
