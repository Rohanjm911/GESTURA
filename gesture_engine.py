import cv2
import mediapipe as mp
import math
import time
import threading
import numpy as np
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyboardController
from smoother import DynamicCursorSmoother
from monitor_manager import MonitorManager

try:
    import winsound
except ImportError:
    winsound = None


class GestureEngine:
    INFERENCE_MAX_WIDTH = 640
    HAND_LOSS_GRACE_SEC = 0.22

    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            model_complexity=1,
            min_detection_confidence=0.65,
            min_tracking_confidence=0.60,
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.mouse = MouseController()
        self.keyboard = KeyboardController()

        # Multi-Monitor Manager (Per-Monitor DPI Aware)
        self.monitors = MonitorManager()

        self.smoother = DynamicCursorSmoother()

        # Resolution-independent palm scale (normalized to frame height)
        self.base_palm_norm = 0.18
        self.smoothed_palm_norm = 0.18
        self._smoothed_box = None
        self._last_frame_shape = None

        # Configurable Control Parameters
        self.box_scale_multiplier = 0.36
        self.smoothing_level = 0.50       # 0.0 (Snappy) to 1.0 (Ultra Smooth)
        self.pinch_sensitivity = 1.0      # 0.6 to 1.5 multiplier
        self.scroll_speed = 1.0           # 0.5 to 3.0 multiplier
        self.is_left_hand = False
        self.flip_camera = True

        # Gesture Enable Toggles
        self.enable_sniper = True
        self.enable_scroll = True
        self.enable_drag = True
        self.enable_right_click = True
        self.enable_screenshot = True
        self.audio_feedback = False

        # Visual Overlay Toggles
        self.show_landmarks = True
        self.show_active_box = True
        self.show_hud_text = True
        self.show_finger_tracker = True
        self.accent_bgr = (255, 210, 0)   # Default Cyan in BGR

        # Runtime State & Temporal Debouncers
        self.last_click_time = 0.0
        self.pinch_start_time = None
        self.fist_start_time = None
        self.is_dragging = False
        self.pinch_click_active = False
        self.right_click_active = False
        self.prev_scroll_y = None
        self._scroll_accum = 0.0
        self._click_confirm_frames = 0
        self._rclick_confirm_frames = 0
        self._pause_confirm_frames = 0

        self.current_action = "Standby"
        self.active_monitor_name = self.monitors.monitors[0].short_label
        self.last_hand_seen = time.time()
        self.hand_detected = False
        self.current_range_pct = 100
        self.click_count = 0

    def set_target_monitor(self, mode_key: str):
        self.monitors.set_target(mode_key)
        self.smoother.reset()

    def refresh_monitors(self):
        monitors = self.monitors.refresh()
        self.smoother.reset()
        return monitors

    def reset_defaults(self):
        self.base_palm_norm = 0.18
        self.smoothed_palm_norm = 0.18
        self._smoothed_box = None
        self.box_scale_multiplier = 0.36
        self.smoothing_level = 0.50
        self.pinch_sensitivity = 1.0
        self.scroll_speed = 1.0
        self.is_left_hand = False
        self.flip_camera = True
        self.enable_sniper = True
        self.enable_scroll = True
        self.enable_drag = True
        self.enable_right_click = True
        self.enable_screenshot = True
        self.audio_feedback = False
        self.show_landmarks = True
        self.show_active_box = True
        self.show_hud_text = True
        self.show_finger_tracker = True
        self.monitors.set_target(MonitorManager.ALL_KEY)
        self.smoother.reset()

    def recalibrate_palm(self):
        if self.hand_detected and self.smoothed_palm_norm > 0.05:
            self.base_palm_norm = self.smoothed_palm_norm
            self._smoothed_box = None
            return True
        return False

    def _play_click_sound(self, freq=1200, dur=25):
        if self.audio_feedback and winsound is not None:
            threading.Thread(
                target=lambda: winsound.Beep(freq, dur),
                daemon=True,
            ).start()

    def _release_drag(self):
        if self.is_dragging:
            try:
                self.mouse.release(Button.left)
            except Exception:
                pass
            self.is_dragging = False
        self.pinch_start_time = None

    def _reset_gesture_debouncers(self):
        self._click_confirm_frames = 0
        self._rclick_confirm_frames = 0
        self._pause_confirm_frames = 0

    def _apply_smoothing(self, sniper_mode=False, pre_click_damping=0.0):
        self.smoother.configure(
            smoothing_level=self.smoothing_level,
            sniper_mode=sniper_mode,
            pre_click_damping=pre_click_damping,
        )

    def _move_cursor_mapped(self, x1: float, y1: float, x_min: float, x_max: float, y_min: float, y_max: float):
        t_left, t_top, t_right, t_bottom = self.monitors.get_target_bounds()
        t_width = max(t_right - t_left, 1)

        # Sub-pixel float interpolation mapped directly to target display bounds
        nx = max(0.0, min(1.0, (x1 - x_min) / max(x_max - x_min, 1e-3)))
        ny = max(0.0, min(1.0, (y1 - y_min) / max(y_max - y_min, 1e-3)))
        raw_x = t_left + nx * (t_right - t_left - 1)
        raw_y = t_top + ny * (t_bottom - t_top - 1)

        span_factor = max(1.0, t_width / 1920.0)
        sx, sy = self.smoother.update(raw_x, raw_y, span_factor=span_factor)
        sx, sy = self.monitors.clamp_to_valid_screen(sx, sy)

        mon = self.monitors.get_monitor_at(sx, sy)
        self.active_monitor_name = mon.short_label

        try:
            self.mouse.position = (sx, sy)
        except Exception:
            pass

    @staticmethod
    def _dist(p1: tuple[float, float], p2: tuple[float, float]) -> float:
        return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

    def _analyze_hand_pose(self, lm_pts: list[tuple[float, float]], palm_px: float) -> tuple[list[int], float]:
        """
        Rotation- and tilt-invariant finger state analysis using wrist-relative distances
        and PIP joint extension angles. Returns (fingers[5], middle_lift_ratio).
        """
        wrist = lm_pts[0]
        fingers = []

        # Thumb: rotation-invariant comparison against pinky MCP (17) and index MCP (5)
        d_thumb_tip_pinky = self._dist(lm_pts[4], lm_pts[17])
        d_thumb_ip_pinky = self._dist(lm_pts[3], lm_pts[17])
        d_thumb_tip_index = self._dist(lm_pts[4], lm_pts[5])
        thumb_up = (
            d_thumb_tip_pinky > d_thumb_ip_pinky * 1.05
            and d_thumb_tip_index > 0.36 * palm_px
        )
        fingers.append(1 if thumb_up else 0)

        # Index, Middle, Ring, Pinky: distance from wrist + PIP straightness check
        middle_lift = 0.0
        for f_idx, (mcp_i, pip_i, tip_i) in enumerate([(5, 6, 8), (9, 10, 12), (13, 14, 16), (17, 18, 20)]):
            mcp = lm_pts[mcp_i]
            pip = lm_pts[pip_i]
            tip = lm_pts[tip_i]

            d_tip = self._dist(tip, wrist)
            d_pip = max(self._dist(pip, wrist), 1e-5)
            d_mcp = max(self._dist(mcp, wrist), 1e-5)
            ext_ratio = d_tip / d_pip

            # Cosine of extension angle at PIP joint (1.0 = straight, <0 = curled)
            v1x, v1y = pip[0] - mcp[0], pip[1] - mcp[1]
            v2x, v2y = tip[0] - pip[0], tip[1] - pip[1]
            mag = max(math.hypot(v1x, v1y) * math.hypot(v2x, v2y), 1e-5)
            cos_ext = (v1x * v2x + v1y * v2y) / mag

            is_up = (ext_ratio > 1.08) and (d_tip > d_mcp * 1.22) and (cos_ext > 0.15)
            fingers.append(1 if is_up else 0)

            if f_idx == 1:  # Middle finger partial lift indicator for pre-click stabilization
                middle_lift = float(np.clip((ext_ratio - 0.94) / 0.16, 0.0, 1.0))

        return fingers, middle_lift

    def _draw_corner_box(self, frame, x_min, y_min, x_max, y_max, color):
        x_min, y_min, x_max, y_max = int(round(x_min)), int(round(y_min)), int(round(x_max)), int(round(y_max))
        # Neo-Brutalist thick ink border + vivid corner brackets
        cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (17, 17, 17), 3)
        cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), color, 1)
        corner_len = 24
        for c_col, thick in [((17, 17, 17), 7), (color, 4)]:
            # Top-Left
            cv2.line(frame, (x_min, y_min), (x_min + corner_len, y_min), c_col, thick)
            cv2.line(frame, (x_min, y_min), (x_min, y_min + corner_len), c_col, thick)
            # Top-Right
            cv2.line(frame, (x_max, y_min), (x_max - corner_len, y_min), c_col, thick)
            cv2.line(frame, (x_max, y_min), (x_max, y_min + corner_len), c_col, thick)
            # Bottom-Left
            cv2.line(frame, (x_min, y_max), (x_min + corner_len, y_max), c_col, thick)
            cv2.line(frame, (x_min, y_max), (x_min, y_max - corner_len), c_col, thick)
            # Bottom-Right
            cv2.line(frame, (x_max, y_max), (x_max - corner_len, y_max), c_col, thick)
            cv2.line(frame, (x_max, y_max), (x_max, y_max - corner_len), c_col, thick)

        # Draw crisp Neo-Brutalist monitor dividers when spanning multiple displays
        dividers = self.monitors.get_normalized_dividers()
        if dividers:
            box_w = x_max - x_min
            for frac in dividers:
                dx = x_min + int(box_w * frac)
                for dy in range(y_min + 10, y_max - 10, 14):
                    cv2.line(frame, (dx, dy), (dx, min(dy + 7, y_max - 6)), (17, 17, 17), 3)
                    cv2.line(frame, (dx, dy), (dx, min(dy + 7, y_max - 6)), color, 1)
            v_left, _, v_right, _ = self.monitors.virtual_bounds
            v_w = max(v_right - v_left, 1)
            for m in self.monitors.monitors:
                center_frac = ((m.left + m.width / 2) - v_left) / v_w
                lx = x_min + int(box_w * center_frac) - 18
                ly = y_max - 26
                cv2.rectangle(frame, (lx + 2, ly + 2), (lx + 38, ly + 22), (17, 17, 17), -1)
                cv2.rectangle(frame, (lx, ly), (lx + 36, ly + 20), color, -1)
                cv2.rectangle(frame, (lx, ly), (lx + 36, ly + 20), (17, 17, 17), 2)
                cv2.putText(
                    frame, f"M{m.index}", (lx + 7, ly + 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (17, 17, 17), 2, cv2.LINE_AA
                )

    def _compute_active_box(self, w: int, h: int, distance_scale: float) -> tuple[float, float, float, float]:
        if self._last_frame_shape != (h, w):
            self._last_frame_shape = (h, w)
            self._smoothed_box = None

        span_w_boost = 1.20 if self.monitors.is_spanning_multiple else 1.0
        box_half_w = min(w * 0.47, (w * self.box_scale_multiplier) * distance_scale * span_w_boost)
        box_half_h = min(h * 0.46, (h * self.box_scale_multiplier) * distance_scale)

        # Slightly lowered ergonomic vertical center reduces arm fatigue reaching top of screen
        center_x = w * 0.50
        center_y = h * 0.52

        target = [
            max(20.0, center_x - box_half_w),
            min(float(w - 20), center_x + box_half_w),
            max(20.0, center_y - box_half_h),
            min(float(h - 20), center_y + box_half_h),
        ]
        if target[1] <= target[0]:
            target[1] = target[0] + 1.0
        if target[3] <= target[2]:
            target[3] = target[2] + 1.0

        if self._smoothed_box is None:
            self._smoothed_box = list(target)
        else:
            # Smooth box transitions so palm-depth fluctuations never jolt cursor mapping
            for i in range(4):
                self._smoothed_box[i] = 0.86 * self._smoothed_box[i] + 0.14 * target[i]

        return tuple(self._smoothed_box)

    def process_frame(self, frame):
        if self.flip_camera:
            frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        # Fast inference path: downscale high-res frames to max 640px wide for MediaPipe
        # (normalized landmarks map back to full-res sub-pixel coordinates with zero accuracy loss)
        if w > self.INFERENCE_MAX_WIDTH:
            scale = self.INFERENCE_MAX_WIDTH / float(w)
            inf_frame = cv2.resize(frame, (self.INFERENCE_MAX_WIDTH, max(1, int(h * scale))), interpolation=cv2.INTER_LINEAR)
        else:
            inf_frame = frame

        rgb_frame = cv2.cvtColor(inf_frame, cv2.COLOR_BGR2RGB)
        rgb_frame.flags.writeable = False
        results = self.hands.process(rgb_frame)
        now = time.time()

        if results and results.multi_hand_landmarks:
            self.hand_detected = True
            self.last_hand_seen = now
            hand_lms = results.multi_hand_landmarks[0]

            if self.show_landmarks:
                self.mp_draw.draw_landmarks(
                    frame, hand_lms, self.mp_hands.HAND_CONNECTIONS,
                    self.mp_draw.DrawingSpec(color=self.accent_bgr, thickness=2, circle_radius=3),
                    self.mp_draw.DrawingSpec(color=(220, 230, 240), thickness=1),
                )

            # Sub-pixel float coordinates (prevents 5-10px quantization jumps on HD/multi-monitors)
            lm_pts = [(lm.x * w, lm.y * h) for lm in hand_lms.landmark]
            if len(lm_pts) < 21:
                return frame, self.current_action

            # Stable resolution-independent palm size (blend of palm length + palm width)
            palm_len_px = self._dist(lm_pts[0], lm_pts[9])
            palm_wid_px = self._dist(lm_pts[5], lm_pts[17])
            raw_palm_norm = max((0.65 * palm_len_px + 0.35 * palm_wid_px) / max(h, 1), 0.04)

            # Deadband + slow EMA so curling fingers does not wobble active box size
            if abs(raw_palm_norm - self.smoothed_palm_norm) > 0.004:
                self.smoothed_palm_norm = 0.88 * self.smoothed_palm_norm + 0.12 * raw_palm_norm

            palm_px = max(self.smoothed_palm_norm * h, 20.0)
            distance_scale = float(np.clip(self.smoothed_palm_norm / max(self.base_palm_norm, 0.05), 0.35, 1.35))
            self.current_range_pct = int(distance_scale * 100)

            x_min, x_max, y_min, y_max = self._compute_active_box(w, h, distance_scale)

            if self.show_active_box:
                self._draw_corner_box(frame, x_min, y_min, x_max, y_max, self.accent_bgr)

            fingers, middle_lift = self._analyze_hand_pose(lm_pts, palm_px)
            x1, y1 = lm_pts[8]    # Index tip (float)
            x2, y2 = lm_pts[12]   # Middle tip (float)
            xt, yt = lm_pts[4]    # Thumb tip (float)
            ix1, iy1 = int(round(x1)), int(round(y1))
            mx, my = int(round(lm_pts[9][0])), int(round(lm_pts[9][1]))

            # Resolution-independent pinch thresholds with Schmitt-trigger hysteresis
            pinch_enter = max(14.0, 0.30 * palm_px * self.pinch_sensitivity)
            pinch_exit = pinch_enter * 1.38
            pinch_thumb_index = self._dist((xt, yt), (x1, y1))

            if self.show_finger_tracker:
                cv2.circle(frame, (ix1, iy1), 9, self.accent_bgr, 2, cv2.LINE_AA)
                cv2.circle(frame, (ix1, iy1), 3, (255, 255, 255), -1, cv2.LINE_AA)

            # Determine active drag continuation with hysteresis (never drops on brief flicker)
            drag_pinch_active = (
                self.enable_drag
                and sum(fingers) != 5
                and (
                    (self.is_dragging and pinch_thumb_index < pinch_exit * 1.22)
                    or (
                        not self.is_dragging
                        and pinch_thumb_index < pinch_enter * 1.08
                        and fingers[2] == 0
                        and fingers[3] == 0
                    )
                )
            )

            # 1. OPEN PALM (5 Fingers): Safe Pause (2-frame confirmation avoids glitch resets)
            if sum(fingers) == 5:
                self._release_drag()
                self.pinch_click_active = False
                self.right_click_active = False
                self.prev_scroll_y = None
                self._scroll_accum = 0.0
                self.fist_start_time = None
                self._click_confirm_frames = 0
                self._rclick_confirm_frames = 0
                self._pause_confirm_frames += 1
                if self._pause_confirm_frames >= 2:
                    self.smoother.reset()
                self.current_action = "Paused (Open Palm)"

            # 2. CLOSED FIST (1.0s Hold): Screenshot Capture
            elif sum(fingers) == 0 and self.enable_screenshot and not self.is_dragging:
                self._release_drag()
                self.pinch_click_active = False
                self.right_click_active = False
                self.prev_scroll_y = None
                self._scroll_accum = 0.0
                self._reset_gesture_debouncers()

                if self.fist_start_time is None:
                    self.fist_start_time = now
                elapsed = now - self.fist_start_time
                pct = min(max(int(elapsed * 100), 0), 100)
                self.current_action = f"Hold Fist: Screenshot ({pct}%)"
                cv2.ellipse(frame, (mx, my), (38, 38), -90, 0, int(360 * (pct / 100)), self.accent_bgr, 4, cv2.LINE_AA)
                if elapsed >= 1.0:
                    try:
                        with self.keyboard.pressed(Key.cmd):
                            with self.keyboard.pressed(Key.shift):
                                self.keyboard.tap("s")
                    except Exception:
                        pass
                    self._play_click_sound(1600, 60)
                    self.fist_start_time = now + 2.0
                    self.current_action = "Screenshot Captured!"

            # 3. THUMB + INDEX PINCH HOLD: Drag & Drop (with hysteresis & midpoint tracking)
            elif drag_pinch_active:
                self.pinch_click_active = False
                self.right_click_active = False
                self.prev_scroll_y = None
                self._scroll_accum = 0.0
                self.fist_start_time = None
                self._reset_gesture_debouncers()

                drag_x, drag_y = (xt + x1) * 0.5, (yt + y1) * 0.5
                if self.show_finger_tracker:
                    cv2.circle(frame, (int(round(drag_x)), int(round(drag_y))), 14, (0, 200, 255), 3, cv2.LINE_AA)

                if self.pinch_start_time is None:
                    self.pinch_start_time = now
                elif (now - self.pinch_start_time > 0.28) and not self.is_dragging:
                    try:
                        self.mouse.press(Button.left)
                    except Exception:
                        pass
                    self._play_click_sound(900, 30)
                    self.is_dragging = True

                if self.is_dragging:
                    self._apply_smoothing(sniper_mode=False)
                    self.current_action = "Dragging Item"
                    self._move_cursor_mapped(drag_x, drag_y, x_min, x_max, y_min, y_max)
                else:
                    self.current_action = "Hold Pinch to Drag..."

            # 4. INDEX UP (or INDEX + PINKY for Precision Sniper Mode)
            elif fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0:
                self._release_drag()
                self.pinch_click_active = False
                self.right_click_active = False
                self.prev_scroll_y = None
                self._scroll_accum = 0.0
                self.fist_start_time = None
                self._reset_gesture_debouncers()

                if self.enable_sniper and fingers[4] == 1:
                    self._apply_smoothing(sniper_mode=True)
                    self.current_action = "Precision Sniper Mode"
                    if self.show_finger_tracker:
                        cv2.circle(frame, (ix1, iy1), 16, (0, 255, 170), 2, cv2.LINE_AA)
                else:
                    # Smooth pre-click damping as middle finger starts lifting toward a click
                    self._apply_smoothing(sniper_mode=False, pre_click_damping=middle_lift * 0.85)
                    self.current_action = "Cursor Navigation"

                self._move_cursor_mapped(x1, y1, x_min, x_max, y_min, y_max)

            # 5. INDEX + MIDDLE: Left Click, Double Click (Hysteresis) & Fractional Smooth Scroll
            elif fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0:
                self._release_drag()
                self.right_click_active = False
                self.fist_start_time = None
                self._rclick_confirm_frames = 0
                self._pause_confirm_frames = 0

                dist_im = self._dist((x1, y1), (x2, y2))
                is_pinched = (
                    (self.pinch_click_active and dist_im < pinch_exit)
                    or (not self.pinch_click_active and dist_im < pinch_enter)
                )

                if is_pinched:
                    self.prev_scroll_y = None
                    self._scroll_accum = 0.0
                    if self.show_finger_tracker:
                        cx, cy = int(round((x1 + x2) * 0.5)), int(round((y1 + y2) * 0.5))
                        cv2.circle(frame, (cx, cy), 14, (0, 255, 120), -1, cv2.LINE_AA)

                    if not self.pinch_click_active:
                        self._click_confirm_frames += 1
                        if self._click_confirm_frames >= 2:
                            self.pinch_click_active = True
                            self._click_confirm_frames = 0
                            if 0.06 < (now - self.last_click_time) < 0.42:
                                try:
                                    self.mouse.click(Button.left, 2)
                                except Exception:
                                    pass
                                self._play_click_sound(1450, 35)
                                self.click_count += 2
                                self.last_click_time = 0.0
                                self.current_action = "Double Click!"
                            else:
                                try:
                                    self.mouse.click(Button.left, 1)
                                except Exception:
                                    pass
                                self._play_click_sound(1150, 25)
                                self.click_count += 1
                                self.last_click_time = now
                                self.current_action = "Left Click"
                    else:
                        self.current_action = "Click (Holding)"

                elif self.enable_scroll and dist_im > pinch_enter * 1.15:
                    self.pinch_click_active = False
                    self._click_confirm_frames = 0
                    scroll_y = (y1 + y2) * 0.5

                    if self.prev_scroll_y is None:
                        self.prev_scroll_y = scroll_y
                        self._scroll_accum = 0.0

                    delta_norm = (self.prev_scroll_y - scroll_y) / palm_px
                    self.prev_scroll_y = scroll_y

                    if abs(delta_norm) > 0.006:
                        self._scroll_accum += delta_norm * 24.0 * self.scroll_speed
                        if abs(self._scroll_accum) >= 1.0:
                            step = int(np.clip(int(self._scroll_accum), -10, 10))
                            self._scroll_accum -= step
                            if step != 0:
                                try:
                                    self.mouse.scroll(0, step)
                                except Exception:
                                    pass
                                self.current_action = f"Scrolling {'Up' if step > 0 else 'Down'}"
                            else:
                                self.current_action = "Smooth Scrolling"
                        else:
                            self.current_action = "Smooth Scrolling"
                    else:
                        self.current_action = "Smooth Scrolling"
                else:
                    self.pinch_click_active = False
                    self._click_confirm_frames = 0
                    self.prev_scroll_y = None
                    self._scroll_accum = 0.0
                    self.current_action = "Ready to Click" if self.enable_scroll else "Scroll Disabled"

            # 6. THREE FINGERS UP (Index + Middle + Ring): Right Click (3-frame debounce)
            elif self.enable_right_click and fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 0:
                self._release_drag()
                self.pinch_click_active = False
                self.prev_scroll_y = None
                self._scroll_accum = 0.0
                self.fist_start_time = None
                self._click_confirm_frames = 0
                self._pause_confirm_frames = 0

                if not self.right_click_active:
                    self._rclick_confirm_frames += 1
                    if self._rclick_confirm_frames >= 3:
                        try:
                            self.mouse.click(Button.right, 1)
                        except Exception:
                            pass
                        self._play_click_sound(850, 30)
                        self.click_count += 1
                        self.right_click_active = True
                        self._rclick_confirm_frames = 0
                        self.last_click_time = now
                        self.current_action = "Right Click"
                else:
                    self.current_action = "Right Click (Holding)"

            else:
                self._release_drag()
                self.pinch_click_active = False
                self.right_click_active = False
                self.prev_scroll_y = None
                self._scroll_accum = 0.0
                self.fist_start_time = None
                self._reset_gesture_debouncers()
                self.current_action = "Tracking Hand"

            # Render Neo-Brutalist HUD badge AFTER gesture state updates so badge is zero-frame delayed
            if self.show_hud_text:
                mon_tag = self.active_monitor_name.replace(" ★", "")
                label_txt = f"{mon_tag.upper()} | {self.current_range_pct}% | {self.current_action.upper()}"
                (tw, th), _ = cv2.getTextSize(label_txt, cv2.FONT_HERSHEY_SIMPLEX, 0.50, 2)
                bx1 = int(round(x_min))
                by2 = max(th + 14, int(round(y_min)) - 6)
                by1 = by2 - th - 10
                bx2 = min(w - 10, bx1 + tw + 16)
                cv2.rectangle(frame, (bx1 + 3, by1 + 3), (bx2 + 3, by2 + 3), (17, 17, 17), -1)
                cv2.rectangle(frame, (bx1, by1), (bx2, by2), self.accent_bgr, -1)
                cv2.rectangle(frame, (bx1, by1), (bx2, by2), (17, 17, 17), 2)
                cv2.putText(
                    frame, label_txt, (bx1 + 8, by2 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.50, (17, 17, 17), 2, cv2.LINE_AA,
                )

        else:
            # Brief hand-loss grace window prevents dropped drags & tracking jumps on motion blur
            missing_for = now - self.last_hand_seen
            if self.hand_detected and missing_for < self.HAND_LOSS_GRACE_SEC:
                self.current_action = "Dragging (Hold)" if self.is_dragging else "Re-acquiring Hand"
            else:
                self.hand_detected = False
                self._release_drag()
                self.pinch_click_active = False
                self.right_click_active = False
                self.prev_scroll_y = None
                self._scroll_accum = 0.0
                self.fist_start_time = None
                self._reset_gesture_debouncers()
                self.current_action = "No Hand Detected"
                self.smoother.reset()

        return frame, self.current_action

    def release(self):
        self._release_drag()
        try:
            self.hands.close()
        except Exception:
            pass
