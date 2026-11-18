import os
import sys
import subprocess

# Auto-redirect to project venv if launched with system Python without activated venv
_venv_python = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv", "Scripts", "python.exe")
if os.path.exists(_venv_python) and os.path.abspath(sys.executable).lower() != os.path.abspath(_venv_python).lower():
    try:
        import pynput
        import mediapipe
        import cv2
        import customtkinter
    except ImportError:
        result = subprocess.run([_venv_python] + sys.argv)
        sys.exit(result.returncode)

import customtkinter as ctk
import cv2
import threading
import time
from PIL import Image
from gesture_engine import GestureEngine
from icons import make_icon

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

# ── NEO-BRUTALIST COLOR PALETTES ─────────────────────────────────────────────
PALETTES = {
    "Acid Pop": {
        "mode": "Light",
        "canvas": "#FFFDF5",
        "sidebar": "#F7F3E3",
        "card": "#FFFFFF",
        "card_sub": "#FFF8DC",
        "video_bg": "#18181B",
        "ink": "#111111",
        "muted": "#4B5563",
        "border": "#111111",
        "shadow": "#111111",
        "primary": "#FFDE00",
        "primary_hover": "#EBC800",
        "primary_ink": "#111111",
        "c1": "#FFDE00",   # Yellow
        "c2": "#34D399",   # Mint
        "c3": "#60A5FA",   # Sky
        "c4": "#FF90E8",   # Pink
        "start_bg": "#34D399",
        "start_hover": "#10B981",
        "stop_bg": "#FF6B6B",
        "stop_hover": "#EF4444",
        "bgr": (0, 222, 255),
    },
    "Gumroad Pink": {
        "mode": "Light",
        "canvas": "#F4FFF8",
        "sidebar": "#E6FAEE",
        "card": "#FFFFFF",
        "card_sub": "#FFF0FB",
        "video_bg": "#18181B",
        "ink": "#111111",
        "muted": "#374151",
        "border": "#111111",
        "shadow": "#111111",
        "primary": "#FF90E8",
        "primary_hover": "#F472D0",
        "primary_ink": "#111111",
        "c1": "#FF90E8",
        "c2": "#FFC900",
        "c3": "#2DD4BF",
        "c4": "#93C5FD",
        "start_bg": "#2DD4BF",
        "start_hover": "#14B8A6",
        "stop_bg": "#FF5C5C",
        "stop_hover": "#E11D48",
        "bgr": (232, 144, 255),
    },
    "Cyber Peach": {
        "mode": "Light",
        "canvas": "#FFF5F0",
        "sidebar": "#FFE8DC",
        "card": "#FFFFFF",
        "card_sub": "#FFF0E6",
        "video_bg": "#18181B",
        "ink": "#111111",
        "muted": "#4B5563",
        "border": "#111111",
        "shadow": "#111111",
        "primary": "#FF7A59",
        "primary_hover": "#F95D38",
        "primary_ink": "#111111",
        "c1": "#FF7A59",
        "c2": "#A3E635",
        "c3": "#38BDF8",
        "c4": "#FDE047",
        "start_bg": "#A3E635",
        "start_hover": "#84CC16",
        "stop_bg": "#FF5C5C",
        "stop_hover": "#DC2626",
        "bgr": (89, 122, 255),
    },
    "Blueprint": {
        "mode": "Light",
        "canvas": "#EFF6FF",
        "sidebar": "#DBEAFE",
        "card": "#FFFFFF",
        "card_sub": "#E0EEFF",
        "video_bg": "#0F172A",
        "ink": "#111111",
        "muted": "#334155",
        "border": "#111111",
        "shadow": "#111111",
        "primary": "#60A5FA",
        "primary_hover": "#3B82F6",
        "primary_ink": "#111111",
        "c1": "#60A5FA",
        "c2": "#FACC15",
        "c3": "#4ADE80",
        "c4": "#FB7185",
        "start_bg": "#4ADE80",
        "start_hover": "#22C55E",
        "stop_bg": "#FB7185",
        "stop_hover": "#F43F5E",
        "bgr": (250, 165, 96),
    },
    "Vapor Brutal": {
        "mode": "Light",
        "canvas": "#F5F3FF",
        "sidebar": "#EDE9FE",
        "card": "#FFFFFF",
        "card_sub": "#F3E8FF",
        "video_bg": "#181326",
        "ink": "#111111",
        "muted": "#4C1D95",
        "border": "#111111",
        "shadow": "#111111",
        "primary": "#C084FC",
        "primary_hover": "#A855F7",
        "primary_ink": "#111111",
        "c1": "#C084FC",
        "c2": "#FDE047",
        "c3": "#5EEAD4",
        "c4": "#F472B6",
        "start_bg": "#5EEAD4",
        "start_hover": "#2DD4BF",
        "stop_bg": "#FB7185",
        "stop_hover": "#E11D48",
        "bgr": (252, 132, 192),
    },
    "Brutal Dark": {
        "mode": "Dark",
        "canvas": "#121212",
        "sidebar": "#1B1B1B",
        "card": "#232323",
        "card_sub": "#2C2C2C",
        "video_bg": "#09090B",
        "ink": "#F8FAFC",
        "muted": "#A1A1AA",
        "border": "#F8FAFC",
        "shadow": "#000000",
        "primary": "#BEF264",
        "primary_hover": "#A3E635",
        "primary_ink": "#111111",
        "c1": "#BEF264",
        "c2": "#22D3EE",
        "c3": "#F472B6",
        "c4": "#FDE047",
        "start_bg": "#BEF264",
        "start_hover": "#A3E635",
        "stop_bg": "#FF5C5C",
        "stop_hover": "#EF4444",
        "bgr": (100, 242, 190),
    },
}

RESOLUTIONS = {
    "1280x720 (HD)":   (1280, 720),
    "640x480 (Fast)":  (640, 480),
    "1920x1080 (FHD)": (1920, 1080),
}


class GestureApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("GESTURA // NEO-BRUTALIST GESTURE STUDIO")
        self.geometry("1290x790")
        self.minsize(1080, 690)

        self.engine = GestureEngine()
        self.is_running = False
        self.is_mini_hud = False
        self.cap = None
        self.camera_source = 0
        self.current_resolution = "1280x720 (HD)"
        self.current_palette_name = "Acid Pop"
        self._current_appearance_mode = "Light"
        self.camera_lock = threading.Lock()
        self._ui_lock = threading.Lock()
        self._ui_pending = False
        self._latest_ui_payload = None
        self._toast_after_id = None
        self._icons = {}

        # Dynamic theme widget registries
        self._themed_cards = []
        self._themed_subcards = []
        self._themed_ink_labels = []
        self._themed_muted_labels = []
        self._themed_shadows = []
        self._themed_sliders = []
        self._themed_switches = []
        self._themed_optmenus = []
        self._palette_buttons = {}

        self.engine.accent_bgr = self.pal["bgr"]
        self.configure(fg_color=self.pal["canvas"])

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self._build_dashboard()

    @property
    def pal(self):
        return PALETTES[self.current_palette_name]

    def _get_icon(self, name: str, color: str, size: int = 32):
        key = (name, color, size)
        if key not in self._icons:
            self._icons[key] = make_icon(name, color, size)
        return self._icons[key]

    def _neo_shadow_box(self, parent, height, bg_color, offset=4, radius=6):
        """Creates a container with an authentic hard offset Neo-Brutalist drop shadow (right & bottom)."""
        outer = ctk.CTkFrame(parent, fg_color=self.pal["shadow"], corner_radius=radius, height=height + offset)
        outer.pack_propagate(False)
        outer.grid_propagate(False)
        self._themed_shadows.append(outer)

        box = ctk.CTkFrame(
            outer, fg_color=bg_color, corner_radius=radius,
            border_width=2, border_color=self.pal["border"]
        )
        box.pack(fill="both", expand=True, padx=(0, offset), pady=(0, offset))
        return outer, box

    def _build_dashboard(self):
        p = self.pal

        # ── LEFT SIDEBAR ─────────────────────────────────────────────────────
        self.sidebar = ctk.CTkFrame(
            self, width=368, corner_radius=0,
            fg_color=p["sidebar"], border_width=3, border_color=p["border"]
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Brand Header Sticker Card (with hard offset shadow)
        brand_outer, self.brand_card = self._neo_shadow_box(self.sidebar, height=78, bg_color=p["primary"], offset=5, radius=6)
        brand_outer.pack(fill="x", padx=18, pady=(18, 12))

        top_brand = ctk.CTkFrame(self.brand_card, fg_color="transparent")
        top_brand.pack(fill="x", padx=12, pady=(10, 0))

        self.brand_label = ctk.CTkLabel(
            top_brand, text="GESTURA",
            font=("Segoe UI Black", 20, "bold"), text_color=p["primary_ink"]
        )
        self.brand_label.pack(side="left")

        self.status_pill = ctk.CTkLabel(
            top_brand, text="STANDBY",
            font=("Segoe UI", 10, "bold"), text_color="#FFFFFF",
            fg_color="#111111", corner_radius=4, padx=8, pady=2
        )
        self.status_pill.pack(side="right", pady=2)

        self.brand_sub = ctk.CTkLabel(
            self.brand_card, text="NEO-BRUTALIST GESTURE STUDIO // MULTI-MONITOR",
            font=("Segoe UI", 9, "bold"), text_color=p["primary_ink"], anchor="w"
        )
        self.brand_sub.pack(fill="x", padx=12, pady=(2, 8))

        # Primary Start/Stop CTA Button with Hard Neo Shadow
        cta_outer = ctk.CTkFrame(self.sidebar, fg_color=p["shadow"], corner_radius=6, height=52)
        cta_outer.pack(fill="x", padx=18, pady=(0, 10))
        cta_outer.pack_propagate(False)
        self._themed_shadows.append(cta_outer)

        self.toggle_btn = ctk.CTkButton(
            cta_outer, text="▶  START GESTURE ENGINE",
            corner_radius=6, border_width=2, border_color=p["border"],
            font=("Segoe UI Black", 13, "bold"),
            fg_color=p["start_bg"], hover_color=p["start_hover"], text_color="#111111",
            command=self.toggle_engine
        )
        self.toggle_btn.pack(fill="both", expand=True, padx=(0, 4), pady=(0, 4))

        # Quick Action Row (Calibrate / Theme Cycle / Reset)
        quick_row = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        quick_row.pack(padx=18, pady=(0, 12), fill="x")
        quick_row.grid_columnconfigure((0, 1, 2), weight=1)

        self.calibrate_btn = ctk.CTkButton(
            quick_row, text="Calibrate", image=self._get_icon("calibrate", "#FFDE00", 18),
            compound="left", height=34, corner_radius=6,
            font=("Segoe UI", 11, "bold"),
            fg_color=p["card"], hover_color=p["primary"], text_color=p["ink"],
            border_width=2, border_color=p["border"],
            command=self.calibrate_palm
        )
        self.calibrate_btn.grid(row=0, column=0, padx=(0, 4), sticky="ew")

        self.cycle_theme_btn = ctk.CTkButton(
            quick_row, text="Colors", image=self._get_icon("palette", "#FF90E8", 18),
            compound="left", height=34, corner_radius=6,
            font=("Segoe UI", 11, "bold"),
            fg_color=p["card"], hover_color=p["primary"], text_color=p["ink"],
            border_width=2, border_color=p["border"],
            command=self.cycle_palette
        )
        self.cycle_theme_btn.grid(row=0, column=1, padx=2, sticky="ew")

        self.reset_btn = ctk.CTkButton(
            quick_row, text="↺ Reset", height=34, corner_radius=6,
            font=("Segoe UI", 11, "bold"),
            fg_color=p["card"], hover_color=p["primary"], text_color=p["ink"],
            border_width=2, border_color=p["border"],
            command=self.reset_all_settings
        )
        self.reset_btn.grid(row=0, column=2, padx=(4, 0), sticky="ew")

        # Tabbed Options Deck
        self.tabs = ctk.CTkTabview(
            self.sidebar, corner_radius=6, border_width=2, border_color=p["border"],
            fg_color=p["card"],
            segmented_button_fg_color=p["border"],
            segmented_button_selected_color=p["primary"],
            segmented_button_selected_hover_color=p["primary_hover"],
            segmented_button_unselected_color=p["card"],
            segmented_button_unselected_hover_color=p["card_sub"],
            text_color=p["ink"]
        )
        self.tabs.pack(padx=16, pady=(0, 16), fill="both", expand=True)

        tab_controls = self.tabs.add("CONTROLS")
        tab_gestures = self.tabs.add("GESTURES")
        tab_display = self.tabs.add("STYLE")

        self._build_controls_tab(tab_controls)
        self._build_gestures_tab(tab_gestures)
        self._build_display_tab(tab_display)

        # ── RIGHT MAIN VIEWPORT ──────────────────────────────────────────────
        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.pack(side="right", fill="both", expand=True, padx=20, pady=18)

        # Top 4 Neo-Brutalist Colored Metric Cards
        self.telemetry_frame = ctk.CTkFrame(self.main_area, fg_color="transparent", height=82)
        self.telemetry_frame.pack(fill="x", pady=(0, 14))
        self.telemetry_frame.pack_propagate(False)
        self.telemetry_frame.grid_columnconfigure(0, weight=3)
        self.telemetry_frame.grid_columnconfigure(1, weight=2)
        self.telemetry_frame.grid_columnconfigure(2, weight=2)
        self.telemetry_frame.grid_columnconfigure(3, weight=2)

        init_mon = self.engine.monitors.monitors[0].short_label
        self.card_action_box, self.card_action = self._create_metric_card(self.telemetry_frame, 0, "ACTIVE GESTURE", "STANDBY", p["c1"])
        self.card_perf_box, self.card_perf = self._create_metric_card(self.telemetry_frame, 1, "PERFORMANCE", "0 FPS • 0 MS", p["c2"])
        self.card_display_box, self.card_display = self._create_metric_card(self.telemetry_frame, 2, "ACTIVE DISPLAY", init_mon.upper(), p["c3"])
        self.card_stats_box, self.card_stats = self._create_metric_card(self.telemetry_frame, 3, "RANGE • CLICKS", "100% • 0", p["c4"])

        # Mini-HUD Bar (Neo-Brutalist Compact Floating Bar)
        self.mini_hud_bar = ctk.CTkFrame(
            self.main_area, height=68, corner_radius=6,
            fg_color=p["primary"], border_width=3, border_color=p["border"]
        )
        self.mini_action_lbl = ctk.CTkLabel(
            self.mini_hud_bar, text="STANDBY",
            font=("Segoe UI Black", 13, "bold"), text_color="#111111"
        )
        self.mini_action_lbl.pack(side="left", padx=14, pady=10)

        self.expand_hud_btn = ctk.CTkButton(
            self.mini_hud_bar, text="EXPAND", width=82, height=32,
            corner_radius=4, border_width=2, border_color="#111111",
            font=("Segoe UI", 11, "bold"),
            fg_color="#FFFFFF", hover_color="#F3F4F6", text_color="#111111",
            command=self.exit_mini_hud
        )
        self.expand_hud_btn.pack(side="right", padx=12, pady=10)

        self.mini_fps_lbl = ctk.CTkLabel(
            self.mini_hud_bar, text="0 FPS",
            font=("Segoe UI", 11, "bold"), text_color="#FFFFFF",
            fg_color="#111111", corner_radius=4, padx=8, pady=3
        )
        self.mini_fps_lbl.pack(side="right", padx=6, pady=10)

        # Video Preview Container (Hard Neo-Brutalist Border + Offset Shadow)
        self.video_outer = ctk.CTkFrame(self.main_area, fg_color=p["shadow"], corner_radius=6)
        self.video_outer.pack(fill="both", expand=True)
        self._themed_shadows.append(self.video_outer)

        self.video_container = ctk.CTkFrame(
            self.video_outer, fg_color=p["video_bg"], corner_radius=6,
            border_width=3, border_color=p["border"]
        )
        self.video_container.pack(fill="both", expand=True, padx=(0, 6), pady=(0, 6))

        self.offline_icon = self._get_icon("camera", p["primary"], 60)
        self.video_label = ctk.CTkLabel(
            self.video_container,
            image=self.offline_icon, compound="top",
            text="\nCAMERA FEED OFFLINE\nCLICK 'START GESTURE ENGINE' TO LAUNCH TRACKING",
            font=("Segoe UI", 14, "bold"), text_color="#E5E7EB", fg_color="transparent"
        )
        self.video_label.pack(fill="both", expand=True, padx=10, pady=10)

        # Bottom Neo-Brutalist Status Strip
        self.footer_outer, self.footer_bar = self._neo_shadow_box(self.main_area, height=40, bg_color=p["card"], offset=4, radius=6)
        self.footer_outer.pack(fill="x", pady=(12, 0))
        self._themed_cards.append(self.footer_bar)

        self.footer_config_lbl = ctk.CTkLabel(
            self.footer_bar, text="", font=("Segoe UI", 11, "bold"), text_color=p["ink"]
        )
        self.footer_config_lbl.pack(side="left", padx=12)
        self._themed_ink_labels.append(self.footer_config_lbl)

        self.footer_toast_lbl = ctk.CTkLabel(
            self.footer_bar, text="READY", font=("Segoe UI", 10, "bold"),
            text_color="#111111", fg_color=p["primary"],
            corner_radius=4, padx=10, pady=2
        )
        self.footer_toast_lbl.pack(side="right", padx=10, pady=6)

        self._update_footer_summary()

    def _create_metric_card(self, parent, col, title, initial_val, fill_color):
        padx = (0, 10) if col < 3 else (0, 0)
        outer, box = self._neo_shadow_box(parent, height=74, bg_color=fill_color, offset=4, radius=6)
        outer.grid(row=0, column=col, padx=padx, sticky="nsew")

        ctk.CTkLabel(
            box, text=title, font=("Segoe UI", 9, "bold"),
            text_color="#111111", anchor="w"
        ).pack(fill="x", padx=12, pady=(9, 0))

        val_lbl = ctk.CTkLabel(
            box, text=initial_val, font=("Segoe UI Black", 14, "bold"),
            text_color="#111111", anchor="w"
        )
        val_lbl.pack(fill="x", padx=12, pady=(1, 8))
        return box, val_lbl

    # ── TAB 1: CONTROLS ──────────────────────────────────────────────────────
    def _build_controls_tab(self, parent):
        p = self.pal
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=2, pady=2)

        # Multi-Monitor Display Target
        mon_hdr = ctk.CTkFrame(scroll, fg_color="transparent")
        mon_hdr.pack(fill="x", pady=(4, 4))
        lbl = ctk.CTkLabel(
            mon_hdr, text="MULTI-MONITOR DISPLAY", font=("Segoe UI", 10, "bold"),
            text_color=p["ink"], anchor="w"
        )
        lbl.pack(side="left")
        self._themed_ink_labels.append(lbl)

        self.refresh_mon_btn = ctk.CTkButton(
            mon_hdr, text="↻ REFRESH", width=74, height=22, corner_radius=4,
            font=("Segoe UI", 9, "bold"), fg_color=p["primary"], hover_color=p["primary_hover"],
            text_color="#111111", border_width=2, border_color=p["border"],
            command=self.refresh_monitors_ui
        )
        self.refresh_mon_btn.pack(side="right")

        mon_card = ctk.CTkFrame(scroll, fg_color=p["card_sub"], corner_radius=6, border_width=2, border_color=p["border"])
        mon_card.pack(fill="x", pady=(0, 8))
        self._themed_subcards.append(mon_card)

        self.monitor_selector_holder = ctk.CTkFrame(mon_card, fg_color="transparent")
        self.monitor_selector_holder.pack(fill="x", padx=8, pady=(8, 4))

        self.monitor_info_lbl = ctk.CTkLabel(
            mon_card, text="", font=("Segoe UI", 10, "bold"), text_color=p["muted"], anchor="w"
        )
        self.monitor_info_lbl.pack(fill="x", padx=10, pady=(0, 8))
        self._themed_muted_labels.append(self.monitor_info_lbl)

        self._populate_monitor_controls()

        # Camera Hardware
        self._section_label(scroll, "CAMERA HARDWARE")

        cam_row = ctk.CTkFrame(scroll, fg_color="transparent")
        cam_row.pack(fill="x", pady=(2, 8))
        cam_row.grid_columnconfigure((0, 1), weight=1)

        cam_col1 = ctk.CTkFrame(cam_row, fg_color="transparent")
        cam_col1.grid(row=0, column=0, padx=(0, 4), sticky="ew")
        l1 = ctk.CTkLabel(cam_col1, text="Source", font=("Segoe UI", 10, "bold"), text_color=p["muted"], anchor="w")
        l1.pack(fill="x")
        self._themed_muted_labels.append(l1)
        self.camera_source_menu = ctk.CTkOptionMenu(
            cam_col1, values=["Camera 0", "Camera 1", "Camera 2", "Camera 3"],
            height=32, corner_radius=6, fg_color=p["card_sub"], button_color=p["primary"],
            button_hover_color=p["primary_hover"], text_color=p["ink"],
            dropdown_fg_color=p["card"], dropdown_text_color=p["ink"],
            font=("Segoe UI", 11, "bold"), command=self.change_camera_source
        )
        self.camera_source_menu.set("Camera 0")
        self.camera_source_menu.pack(fill="x", pady=(2, 0))
        self._themed_optmenus.append(self.camera_source_menu)

        cam_col2 = ctk.CTkFrame(cam_row, fg_color="transparent")
        cam_col2.grid(row=0, column=1, padx=(4, 0), sticky="ew")
        l2 = ctk.CTkLabel(cam_col2, text="Resolution", font=("Segoe UI", 10, "bold"), text_color=p["muted"], anchor="w")
        l2.pack(fill="x")
        self._themed_muted_labels.append(l2)
        self.resolution_menu = ctk.CTkOptionMenu(
            cam_col2, values=list(RESOLUTIONS.keys()),
            height=32, corner_radius=6, fg_color=p["card_sub"], button_color=p["primary"],
            button_hover_color=p["primary_hover"], text_color=p["ink"],
            dropdown_fg_color=p["card"], dropdown_text_color=p["ink"],
            font=("Segoe UI", 11, "bold"), command=self.change_resolution
        )
        self.resolution_menu.set(self.current_resolution)
        self.resolution_menu.pack(fill="x", pady=(2, 0))
        self._themed_optmenus.append(self.resolution_menu)

        # Dominant Hand
        self._section_label(scroll, "HAND DOMINANCE")
        self.hand_mode = ctk.CTkSegmentedButton(
            scroll, values=["Right Hand", "Left Hand"], height=34, corner_radius=6,
            fg_color=p["border"], selected_color=p["primary"],
            selected_hover_color=p["primary_hover"],
            unselected_color=p["card_sub"], unselected_hover_color=p["card"],
            text_color=p["ink"], font=("Segoe UI", 11, "bold"),
            command=self.change_hand_mode
        )
        self.hand_mode.set("Right Hand")
        self.hand_mode.pack(fill="x", pady=(2, 10))

        # Tracking Sliders
        self._section_label(scroll, "TRACKING & PRECISION")

        self.reach_slider, self.reach_val_lbl = self._add_slider(
            scroll, "Reach Sensitivity (Box)", 0.20, 0.45, 0.36,
            lambda v: f"{int(v * 100)}%", self._on_reach_change
        )
        self.smooth_slider, self.smooth_val_lbl = self._add_slider(
            scroll, "Cursor Smoothing", 0.0, 1.0, 0.50,
            lambda v: f"{int(v * 100)}%", self._on_smooth_change
        )
        self.pinch_slider, self.pinch_val_lbl = self._add_slider(
            scroll, "Pinch Tolerance", 0.60, 1.50, 1.00,
            lambda v: f"{v:.2f}x", self._on_pinch_change
        )
        self.scroll_slider, self.scroll_val_lbl = self._add_slider(
            scroll, "Scroll Speed", 0.50, 3.00, 1.00,
            lambda v: f"{v:.1f}x", self._on_scroll_change
        )

    # ── TAB 2: GESTURES ──────────────────────────────────────────────────────
    def _build_gestures_tab(self, parent):
        p = self.pal
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=2, pady=2)

        self._section_label(scroll, "CORE ALWAYS-ON GESTURES")

        for icon_name, icon_color, title, subtitle in [
            ("cursor", "#FFDE00", "Cursor Navigation", "Extend Index finger only"),
            ("click", "#34D399", "Left & Double Click", "Pinch Index + Middle tips"),
            ("pause", "#FB923C", "Instant Safe Pause", "Open Palm (all 5 fingers)"),
        ]:
            card = ctk.CTkFrame(
                scroll, fg_color=p["card_sub"], corner_radius=6,
                border_width=2, border_color=p["border"]
            )
            card.pack(fill="x", pady=4)
            self._themed_subcards.append(card)

            icon_img = self._get_icon(icon_name, icon_color, 38)
            ctk.CTkLabel(card, text="", image=icon_img).pack(side="left", padx=(8, 8), pady=6)

            mid = ctk.CTkFrame(card, fg_color="transparent")
            mid.pack(side="left", fill="x", expand=True, pady=6)
            t_lbl = ctk.CTkLabel(mid, text=title, font=("Segoe UI", 11, "bold"), text_color=p["ink"], anchor="w")
            t_lbl.pack(fill="x")
            self._themed_ink_labels.append(t_lbl)
            s_lbl = ctk.CTkLabel(mid, text=subtitle, font=("Segoe UI", 10), text_color=p["muted"], anchor="w")
            s_lbl.pack(fill="x")
            self._themed_muted_labels.append(s_lbl)

            ctk.CTkLabel(
                card, text="CORE", font=("Segoe UI", 9, "bold"),
                text_color="#111111", fg_color=icon_color,
                corner_radius=4, padx=7, pady=2
            ).pack(side="right", padx=(4, 8))

        self._section_label(scroll, "CUSTOMIZABLE GESTURES")

        self.sw_sniper = self._add_toggle(
            scroll, "Precision Sniper Mode", "Index + Pinky up for fine aim", True,
            lambda: setattr(self.engine, "enable_sniper", bool(self.sw_sniper.get())),
            icon_name="sniper", icon_color="#2DD4BF"
        )
        self.sw_scroll = self._add_toggle(
            scroll, "Smooth Scrolling", "Index + Middle apart, move up/down", True,
            lambda: setattr(self.engine, "enable_scroll", bool(self.sw_scroll.get())),
            icon_name="scroll", icon_color="#60A5FA"
        )
        self.sw_drag = self._add_toggle(
            scroll, "Drag & Drop", "Hold Thumb + Index pinch (>0.3s)", True,
            lambda: setattr(self.engine, "enable_drag", bool(self.sw_drag.get())),
            icon_name="drag", icon_color="#C084FC"
        )
        self.sw_rclick = self._add_toggle(
            scroll, "Right Click", "Raise Index + Middle + Ring", True,
            lambda: setattr(self.engine, "enable_right_click", bool(self.sw_rclick.get())),
            icon_name="right_click", icon_color="#FF90E8"
        )
        self.sw_screenshot = self._add_toggle(
            scroll, "Screenshot Capture", "Hold Closed Fist for 1.0s", True,
            lambda: setattr(self.engine, "enable_screenshot", bool(self.sw_screenshot.get())),
            icon_name="screenshot", icon_color="#FACC15"
        )

    # ── TAB 3: STYLE & DISPLAY ───────────────────────────────────────────────
    def _build_display_tab(self, parent):
        p = self.pal
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=2, pady=2)

        # Interactive 2x3 Neo-Brutalist Color Swatch Grid
        self._section_label(scroll, "NEO-BRUTALIST COLOR PALETTES")

        swatch_grid = ctk.CTkFrame(scroll, fg_color="transparent")
        swatch_grid.pack(fill="x", pady=(2, 10))
        swatch_grid.grid_columnconfigure((0, 1), weight=1)

        for idx, (pname, pdata) in enumerate(PALETTES.items()):
            r, c = divmod(idx, 2)
            btn = ctk.CTkButton(
                swatch_grid, text=pname.upper(), height=36, corner_radius=6,
                fg_color=pdata["primary"], hover_color=pdata["primary_hover"],
                text_color="#111111", font=("Segoe UI", 10, "bold"),
                border_width=3 if pname == self.current_palette_name else 2,
                border_color="#111111",
                command=lambda n=pname: self.apply_palette(n)
            )
            btn.grid(row=r, column=c, padx=3, pady=3, sticky="ew")
            self._palette_buttons[pname] = btn

        self._section_label(scroll, "WORKSPACE & FEEDBACK")

        self.hud_switch = self._add_toggle(
            scroll, "Floating Mini-HUD", "Compact always-on-top status bar", False,
            self.toggle_mini_hud, icon_name="hud", icon_color="#38BDF8"
        )
        self.sw_mirror = self._add_toggle(
            scroll, "Mirror Camera Feed", "Selfie horizontal flip", True,
            self._on_mirror_toggle, icon_name="mirror", icon_color="#A78BFA"
        )
        self.sw_audio = self._add_toggle(
            scroll, "Audio Click Cue", "Subtle crisp beep on clicks", False,
            lambda: setattr(self.engine, "audio_feedback", bool(self.sw_audio.get())),
            icon_name="audio", icon_color="#4ADE80"
        )

        self._section_label(scroll, "VIDEO OVERLAYS")

        self.sw_landmarks = self._add_toggle(
            scroll, "Hand Skeleton", "Render 21 MediaPipe landmarks", True,
            lambda: setattr(self.engine, "show_landmarks", bool(self.sw_landmarks.get())),
            icon_name="skeleton", icon_color="#2DD4BF"
        )
        self.sw_box = self._add_toggle(
            scroll, "Active Control Box", "Show adaptive boundary + M1/M2", True,
            lambda: setattr(self.engine, "show_active_box", bool(self.sw_box.get())),
            icon_name="box", icon_color="#FFDE00"
        )
        self.sw_hud_text = self._add_toggle(
            scroll, "On-Video Sticker HUD", "Neo-Brutalist badge on camera", True,
            lambda: setattr(self.engine, "show_hud_text", bool(self.sw_hud_text.get())),
            icon_name="telemetry", icon_color="#60A5FA"
        )
        self.sw_tracker = self._add_toggle(
            scroll, "Fingertip Tracker Ring", "Highlight index & pinch points", True,
            lambda: setattr(self.engine, "show_finger_tracker", bool(self.sw_tracker.get())),
            icon_name="tracker", icon_color="#FF90E8"
        )

    # ── UI HELPER BUILDERS ───────────────────────────────────────────────────
    def _section_label(self, parent, text):
        lbl = ctk.CTkLabel(
            parent, text=text, font=("Segoe UI", 10, "bold"),
            text_color=self.pal["ink"], anchor="w"
        )
        lbl.pack(fill="x", pady=(10, 4))
        self._themed_ink_labels.append(lbl)

    def _add_slider(self, parent, label, from_, to_, initial, fmt_fn, callback):
        p = self.pal
        box = ctk.CTkFrame(parent, fg_color=p["card_sub"], corner_radius=6, border_width=2, border_color=p["border"])
        box.pack(fill="x", pady=4)
        self._themed_subcards.append(box)

        top = ctk.CTkFrame(box, fg_color="transparent")
        top.pack(fill="x", padx=10, pady=(7, 2))
        l = ctk.CTkLabel(top, text=label, font=("Segoe UI", 11, "bold"), text_color=p["ink"])
        l.pack(side="left")
        self._themed_ink_labels.append(l)

        val_lbl = ctk.CTkLabel(
            top, text=fmt_fn(initial), font=("Segoe UI", 10, "bold"),
            text_color="#111111", fg_color=p["primary"], corner_radius=4, padx=7, pady=1
        )
        val_lbl.pack(side="right")

        slider = ctk.CTkSlider(
            box, from_=from_, to=to_, height=18,
            fg_color="#D1D5DB", progress_color=p["primary"],
            button_color="#111111", button_hover_color=p["primary_hover"],
            command=lambda v: (val_lbl.configure(text=fmt_fn(float(v))), callback(float(v)))
        )
        slider.set(initial)
        slider.pack(fill="x", padx=10, pady=(4, 10))
        self._themed_sliders.append((slider, val_lbl))
        return slider, val_lbl

    def _add_toggle(self, parent, title, subtitle, initial, command, icon_name=None, icon_color="#FFDE00"):
        p = self.pal
        box = ctk.CTkFrame(parent, fg_color=p["card_sub"], corner_radius=6, border_width=2, border_color=p["border"])
        box.pack(fill="x", pady=4)
        self._themed_subcards.append(box)

        if icon_name:
            hand_icons = {"cursor", "click", "pause", "sniper", "scroll", "drag", "right_click", "screenshot"}
            icon_sz = 38 if icon_name in hand_icons else 34
            icon_img = self._get_icon(icon_name, icon_color, icon_sz)
            ctk.CTkLabel(box, text="", image=icon_img).pack(side="left", padx=(8, 8), pady=6)

        left = ctk.CTkFrame(box, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True, padx=(0 if icon_name else 10, 4), pady=6)
        t_lbl = ctk.CTkLabel(left, text=title, font=("Segoe UI", 11, "bold"), text_color=p["ink"], anchor="w")
        t_lbl.pack(fill="x")
        self._themed_ink_labels.append(t_lbl)
        s_lbl = ctk.CTkLabel(left, text=subtitle, font=("Segoe UI", 10), text_color=p["muted"], anchor="w")
        s_lbl.pack(fill="x")
        self._themed_muted_labels.append(s_lbl)

        sw = ctk.CTkSwitch(
            box, text="", width=42,
            fg_color="#D1D5DB", progress_color=p["primary"],
            button_color="#111111", button_hover_color="#333333",
            border_width=2, border_color="#111111",
            command=command
        )
        if initial:
            sw.select()
        sw.pack(side="right", padx=(0, 8))
        self._themed_switches.append(sw)
        return sw

    # ── LIVE PALETTE SWITCHER ────────────────────────────────────────────────
    def cycle_palette(self):
        names = list(PALETTES.keys())
        nxt = names[(names.index(self.current_palette_name) + 1) % len(names)]
        self.apply_palette(nxt)

    def apply_palette(self, name: str):
        if name not in PALETTES:
            return
        self.current_palette_name = name
        p = self.pal
        if p["mode"] != self._current_appearance_mode:
            self._current_appearance_mode = p["mode"]
            ctk.set_appearance_mode(p["mode"])
        self.engine.accent_bgr = p["bgr"]

        # Main surfaces & borders
        self.configure(fg_color=p["canvas"])
        self.sidebar.configure(fg_color=p["sidebar"], border_color=p["border"])
        self.brand_card.configure(fg_color=p["primary"], border_color=p["border"])
        self.brand_label.configure(text_color=p["primary_ink"])
        self.brand_sub.configure(text_color=p["primary_ink"])

        # Shadows
        for sh in self._themed_shadows:
            if sh.winfo_exists():
                sh.configure(fg_color=p["shadow"])

        # Cards & subcards
        for c in self._themed_cards:
            if c.winfo_exists():
                c.configure(fg_color=p["card"], border_color=p["border"])
        for sc in self._themed_subcards:
            if sc.winfo_exists():
                sc.configure(fg_color=p["card_sub"], border_color=p["border"])

        # Labels
        for l in self._themed_ink_labels:
            if l.winfo_exists():
                l.configure(text_color=p["ink"])
        for l in self._themed_muted_labels:
            if l.winfo_exists():
                l.configure(text_color=p["muted"])

        # CTA & Quick Buttons
        if self.is_running:
            self.toggle_btn.configure(fg_color=p["stop_bg"], hover_color=p["stop_hover"], border_color=p["border"])
        else:
            self.toggle_btn.configure(fg_color=p["start_bg"], hover_color=p["start_hover"], border_color=p["border"])

        for btn in (self.calibrate_btn, self.cycle_theme_btn, self.reset_btn):
            btn.configure(fg_color=p["card"], hover_color=p["primary"], text_color=p["ink"], border_color=p["border"])
        self.refresh_mon_btn.configure(fg_color=p["primary"], hover_color=p["primary_hover"], border_color=p["border"])

        # Tabs & Segmented Buttons
        self.tabs.configure(
            fg_color=p["card"], border_color=p["border"],
            segmented_button_fg_color=p["border"],
            segmented_button_selected_color=p["primary"],
            segmented_button_selected_hover_color=p["primary_hover"],
            segmented_button_unselected_color=p["card"],
            segmented_button_unselected_hover_color=p["card_sub"],
            text_color=p["ink"]
        )
        self.hand_mode.configure(
            fg_color=p["border"], selected_color=p["primary"],
            selected_hover_color=p["primary_hover"],
            unselected_color=p["card_sub"], unselected_hover_color=p["card"],
            text_color=p["ink"]
        )
        if hasattr(self, "monitor_seg") and self.monitor_seg.winfo_exists():
            self.monitor_seg.configure(
                fg_color=p["border"], selected_color=p["primary"],
                selected_hover_color=p["primary_hover"],
                unselected_color=p["card"], unselected_hover_color=p["card_sub"],
                text_color=p["ink"]
            )

        # Option Menus
        for om in self._themed_optmenus:
            if om.winfo_exists():
                om.configure(
                    fg_color=p["card_sub"], button_color=p["primary"],
                    button_hover_color=p["primary_hover"], text_color=p["ink"],
                    dropdown_fg_color=p["card"], dropdown_text_color=p["ink"]
                )

        # Sliders & Switches
        for sl, lbl in self._themed_sliders:
            if sl.winfo_exists():
                sl.configure(progress_color=p["primary"], button_hover_color=p["primary_hover"])
                lbl.configure(fg_color=p["primary"])
        for sw in self._themed_switches:
            if sw.winfo_exists():
                sw.configure(progress_color=p["primary"])

        # 4 Telemetry Cards
        self.card_action_box.configure(fg_color=p["c1"], border_color=p["border"])
        self.card_perf_box.configure(fg_color=p["c2"], border_color=p["border"])
        self.card_display_box.configure(fg_color=p["c3"], border_color=p["border"])
        self.card_stats_box.configure(fg_color=p["c4"], border_color=p["border"])

        # Mini-HUD, Video Frame & Footer Toast
        self.mini_hud_bar.configure(fg_color=p["primary"], border_color=p["border"])
        self.video_container.configure(fg_color=p["video_bg"], border_color=p["border"])
        self.footer_toast_lbl.configure(fg_color=p["primary"])
        self.offline_icon = self._get_icon("camera", p["primary"], 60)
        if not self.is_running and self.video_label.winfo_exists():
            self.video_label.configure(image=self.offline_icon)
            self.video_label.image = self.offline_icon

        # Highlight active palette swatch button
        for pname, pbtn in self._palette_buttons.items():
            pbtn.configure(
                border_width=4 if pname == name else 2,
                border_color="#FFFFFF" if (p["mode"] == "Dark" and pname == name) else "#111111"
            )

        self._show_toast(f"PALETTE: {name.upper()}")

    # ── MULTI-MONITOR CONTROLS ───────────────────────────────────────────────
    def _populate_monitor_controls(self):
        p = self.pal
        for w in self.monitor_selector_holder.winfo_children():
            w.destroy()

        mons = self.engine.monitors.monitors
        self._monitor_label_to_key = {}
        labels = []

        if len(mons) > 1:
            all_lbl = f"ALL ({len(mons)}X)"
            labels.append(all_lbl)
            self._monitor_label_to_key[all_lbl] = self.engine.monitors.ALL_KEY

        for m in mons:
            lbl = f"M{m.index} ★" if m.is_primary else f"M{m.index}"
            labels.append(lbl)
            self._monitor_label_to_key[lbl] = str(m.index)

        self.monitor_seg = ctk.CTkSegmentedButton(
            self.monitor_selector_holder, values=labels, height=32, corner_radius=6,
            fg_color=p["border"], selected_color=p["primary"],
            selected_hover_color=p["primary_hover"],
            unselected_color=p["card"], unselected_hover_color=p["card_sub"],
            text_color=p["ink"], font=("Segoe UI", 11, "bold"),
            command=self.change_target_monitor
        )

        active_key = self.engine.monitors.target_mode
        selected_lbl = labels[0]
        for lbl, key in self._monitor_label_to_key.items():
            if key == active_key:
                selected_lbl = lbl
                break
        self.monitor_seg.set(selected_lbl)
        self.monitor_seg.pack(fill="x")
        self._update_monitor_info_text()

    def _update_monitor_info_text(self):
        left, top, right, bottom = self.engine.monitors.get_target_bounds()
        w, h = right - left, bottom - top
        count = len(self.engine.monitors.monitors)
        if self.engine.monitors.is_spanning_multiple:
            txt = f"SPAN {w}×{h} ({count} DISPLAYS) • ORIGIN ({left}, {top})"
        else:
            lbl = self.engine.monitors.get_target_label().upper()
            txt = f"{lbl} • ORIGIN ({left}, {top})"
        if hasattr(self, "monitor_info_lbl") and self.monitor_info_lbl.winfo_exists():
            self.monitor_info_lbl.configure(text=txt)

    def change_target_monitor(self, choice):
        key = self._monitor_label_to_key.get(choice, self.engine.monitors.ALL_KEY)
        self.engine.set_target_monitor(key)
        self._update_monitor_info_text()
        self._update_footer_summary()
        self._show_toast(f"DISPLAY: {choice}")

    def refresh_monitors_ui(self):
        mons = self.engine.refresh_monitors()
        self._populate_monitor_controls()
        self._update_footer_summary()
        self._show_toast(f"DETECTED {len(mons)} DISPLAY(S)")

    # ── EVENT HANDLERS ───────────────────────────────────────────────────────
    def _show_toast(self, msg, duration_ms=3000):
        if hasattr(self, "footer_toast_lbl") and self.footer_toast_lbl.winfo_exists():
            self.footer_toast_lbl.configure(text=msg.upper())
            if self._toast_after_id:
                try:
                    self.after_cancel(self._toast_after_id)
                except Exception:
                    pass
            self._toast_after_id = self.after(
                duration_ms,
                lambda: self.footer_toast_lbl.configure(text="READY") if self.footer_toast_lbl.winfo_exists() else None
            )

    def _update_footer_summary(self):
        hand = "LEFT HAND" if self.engine.is_left_hand else "RIGHT HAND"
        mirror = "MIRROR ON" if self.engine.flip_camera else "MIRROR OFF"
        res_short = self.current_resolution.split(" ")[0]
        mon_count = len(self.engine.monitors.monitors)
        mon_txt = f"SPAN {mon_count}X" if self.engine.monitors.is_spanning_multiple else self.engine.monitors.get_target_label().split("(")[0].strip().upper()
        summary = f"{mon_txt}  •  CAM {self.camera_source} ({res_short})  •  {hand}  •  {mirror}"
        if hasattr(self, "footer_config_lbl") and self.footer_config_lbl.winfo_exists():
            self.footer_config_lbl.configure(text=summary)

    def _on_reach_change(self, val):
        self.engine.box_scale_multiplier = val

    def _on_smooth_change(self, val):
        self.engine.smoothing_level = val

    def _on_pinch_change(self, val):
        self.engine.pinch_sensitivity = val

    def _on_scroll_change(self, val):
        self.engine.scroll_speed = val

    def _on_mirror_toggle(self):
        self.engine.flip_camera = bool(self.sw_mirror.get())
        self._update_footer_summary()

    def change_hand_mode(self, choice):
        self.engine.is_left_hand = (choice == "Left Hand")
        self._update_footer_summary()
        self._show_toast(f"MODE: {choice}")

    def calibrate_palm(self):
        if self.engine.recalibrate_palm():
            self._show_toast("DISTANCE CALIBRATED!")
        else:
            self._show_toast("SHOW HAND TO CALIBRATE")

    def reset_all_settings(self):
        self.engine.reset_defaults()
        self.hand_mode.set("Right Hand")
        self.reach_slider.set(0.36)
        self.reach_val_lbl.configure(text="36%")
        self.smooth_slider.set(0.50)
        self.smooth_val_lbl.configure(text="50%")
        self.pinch_slider.set(1.00)
        self.pinch_val_lbl.configure(text="1.00x")
        self.scroll_slider.set(1.00)
        self.scroll_val_lbl.configure(text="1.0x")

        for sw in [
            self.sw_sniper, self.sw_scroll, self.sw_drag, self.sw_rclick, self.sw_screenshot,
            self.sw_mirror, self.sw_landmarks, self.sw_box, self.sw_hud_text, self.sw_tracker
        ]:
            sw.select()
        self.sw_audio.deselect()
        self._populate_monitor_controls()
        self._update_footer_summary()
        self._show_toast("DEFAULTS RESTORED")

    def change_camera_source(self, choice):
        source = int(choice.replace("Camera ", ""))
        if not self.is_running:
            self.camera_source = source
            self._update_footer_summary()
            return

        new_cap = self._open_camera(source)
        if new_cap is None:
            self.camera_source_menu.set(f"Camera {self.camera_source}")
            self._show_toast(f"CAM {source} UNAVAILABLE")
            return

        with self.camera_lock:
            self.camera_source = source
            old_cap = self.cap if self.is_running else None
            if self.is_running:
                self.cap = new_cap
        if not self.is_running:
            new_cap.release()
        if old_cap is not None:
            old_cap.release()
        self._update_footer_summary()
        self._show_toast(f"CAMERA {source} ACTIVE")

    def change_resolution(self, choice):
        self.current_resolution = choice
        w, h = RESOLUTIONS[choice]
        with self.camera_lock:
            if self.cap is not None and self.cap.isOpened():
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
        self._update_footer_summary()
        self._show_toast(f"RES: {w}×{h}")

    def _open_camera(self, source):
        cap = cv2.VideoCapture(source, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            cap.release()
            return None
        # Minimize capture buffer latency and request MJPG for high-FPS HD webcams
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        w, h = RESOLUTIONS.get(self.current_resolution, (1280, 720))
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
        cap.set(cv2.CAP_PROP_FPS, 60)
        return cap

    def exit_mini_hud(self):
        self.hud_switch.deselect()
        self.toggle_mini_hud()

    def toggle_mini_hud(self):
        if self.hud_switch.get() == 1:
            self.is_mini_hud = True
            self.sidebar.pack_forget()
            self.telemetry_frame.pack_forget()
            self.video_outer.pack_forget()
            self.footer_outer.pack_forget()
            self.mini_hud_bar.pack(fill="both", expand=True)
            self.minsize(430, 90)
            self.geometry("470x100")
            self.attributes("-topmost", True)
        else:
            self.is_mini_hud = False
            self.mini_hud_bar.pack_forget()
            self.attributes("-topmost", False)
            self.minsize(1080, 690)
            self.geometry("1290x790")
            self.sidebar.pack(side="left", fill="y")
            self.telemetry_frame.pack(fill="x", pady=(0, 14))
            self.video_outer.pack(fill="both", expand=True)
            self.footer_outer.pack(fill="x", pady=(12, 0))

    # ── ENGINE LIFECYCLE ─────────────────────────────────────────────────────
    def toggle_engine(self):
        p = self.pal
        if not self.is_running:
            self.cap = self._open_camera(self.camera_source)
            if self.cap is None:
                self._show_toast(f"CAM {self.camera_source} ERROR")
                self.card_action.configure(text=f"CAM {self.camera_source} ERROR")
                return
            self.is_running = True
            self.engine.smoother.reset()
            self.engine.last_hand_seen = time.time()
            with self._ui_lock:
                self._ui_pending = False
                self._latest_ui_payload = None
            self.toggle_btn.configure(text="■  STOP GESTURE ENGINE", fg_color=p["stop_bg"], hover_color=p["stop_hover"])
            self.status_pill.configure(text="LIVE", fg_color="#10B981", text_color="#111111")
            self._show_toast("ENGINE STARTED")
            threading.Thread(target=self.video_loop, daemon=True).start()
        else:
            self.stop_engine()

    def stop_engine(self):
        p = self.pal
        self.is_running = False
        self.engine._release_drag()
        with self._ui_lock:
            self._ui_pending = False
            self._latest_ui_payload = None
        with self.camera_lock:
            if self.cap:
                self.cap.release()
                self.cap = None
        if hasattr(self, "toggle_btn") and self.toggle_btn.winfo_exists():
            self.toggle_btn.configure(text="▶  START GESTURE ENGINE", fg_color=p["start_bg"], hover_color=p["start_hover"])
        if hasattr(self, "status_pill") and self.status_pill.winfo_exists():
            self.status_pill.configure(text="STANDBY", fg_color="#111111", text_color="#FFFFFF")
        if hasattr(self, "video_label") and self.video_label.winfo_exists():
            self.video_label.configure(
                image=self.offline_icon, compound="top",
                text="\nCAMERA FEED OFFLINE\nCLICK 'START GESTURE ENGINE' TO LAUNCH TRACKING"
            )
            self.video_label.image = self.offline_icon
        if hasattr(self, "card_action") and self.card_action.winfo_exists():
            self.card_action.configure(text="STANDBY")
            self.card_perf.configure(text="0 FPS • 0 MS")
        if hasattr(self, "mini_action_lbl") and self.mini_action_lbl.winfo_exists():
            self.mini_action_lbl.configure(text="STANDBY")
            self.mini_fps_lbl.configure(text="0 FPS")
        self._show_toast("ENGINE STOPPED")

    def video_loop(self):
        prev_time = time.perf_counter()
        fps_ema = 30.0
        while self.is_running:
            t0 = time.perf_counter()
            with self.camera_lock:
                cap = self.cap
                if cap is None or not cap.isOpened():
                    break
                ret, frame = cap.read()
            if not ret or frame is None:
                time.sleep(0.005)
                continue

            processed_frame, action = self.engine.process_frame(frame)
            curr_time = time.perf_counter()
            latency_ms = int((curr_time - t0) * 1000)

            inst_fps = 1.0 / max(curr_time - prev_time, 0.001)
            fps_ema = 0.80 * fps_ema + 0.20 * min(inst_fps, 120.0)
            fps = int(round(fps_ema))
            prev_time = curr_time

            if not self.is_running:
                break

            # Coalesce UI updates so Tkinter rendering never creates frame-queue lag behind tracking
            with self._ui_lock:
                should_render = not self._ui_pending
                if should_render:
                    self._ui_pending = True

            if should_render:
                img = None
                if not self.is_mini_hud:
                    rgb_img = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(rgb_img)

                with self._ui_lock:
                    self._latest_ui_payload = (
                        img, action, fps, latency_ms,
                        self.engine.active_monitor_name,
                        self.engine.current_range_pct, self.engine.click_count,
                    )
                try:
                    self.after(0, self._flush_ui_update)
                except Exception:
                    with self._ui_lock:
                        self._ui_pending = False
                    break

    def _flush_ui_update(self):
        with self._ui_lock:
            payload = self._latest_ui_payload
            self._latest_ui_payload = None
            self._ui_pending = False
        if payload is not None:
            self.update_ui(*payload)

    def update_ui(self, img, action, fps, latency_ms, active_mon, range_pct, clicks):
        if not self.is_running:
            return
        try:
            if not self.is_mini_hud:
                if img is not None and self.video_label.winfo_exists():
                    cw = max(self.video_container.winfo_width() - 20, 640)
                    ch = max(self.video_container.winfo_height() - 20, 400)
                    iw, ih = img.size
                    scale = min(cw / iw, ch / ih)
                    tw, th = max(int(iw * scale), 320), max(int(ih * scale), 200)

                    ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(tw, th))
                    self.video_label.configure(image=ctk_img, text="")
                    self.video_label.image = ctk_img

                self.card_action.configure(text=action.upper())
                self.card_perf.configure(text=f"{fps} FPS • {latency_ms} MS")
                self.card_display.configure(text=active_mon.upper())
                self.card_stats.configure(text=f"{range_pct}% • {clicks}")
            else:
                self.mini_action_lbl.configure(text=f"{active_mon.upper()} | {action.upper()}")
                self.mini_fps_lbl.configure(text=f"{fps} FPS")
        except Exception:
            pass

    def on_closing(self):
        self.stop_engine()
        self.engine.release()
        self.destroy()


if __name__ == "__main__":
    try:
        import ctypes
        user32 = ctypes.windll.user32
        hdesk = user32.OpenDesktopW("Default", 0, False, 0x01FF)
        if hdesk:
            user32.SetThreadDesktop(hdesk)
    except Exception:
        pass

    app = GestureApp()
    app.mainloop()
