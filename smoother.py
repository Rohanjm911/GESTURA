import math
import time


def _smoothing_factor(dt: float, cutoff: float) -> float:
    r = 2.0 * math.pi * max(cutoff, 1e-4) * dt
    return r / (r + 1.0)


class DynamicCursorSmoother:
    """
    Framerate-independent, isotropic One-Euro Filter with soft micro-jitter deadzone.
    - Ultra-steady at low hand velocity (eliminates webcam landmark tremor).
    - Zero-lag snappy tracking during fast sweeps across single or multi-monitor setups.
    - Supports Precision Sniper Mode and smooth pre-click damping.
    """

    def __init__(
        self,
        min_cutoff: float = 1.4,
        beta: float = 15.0,
        d_cutoff: float = 2.5,
        deadzone_px: float = 2.4,
    ):
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff
        self.deadzone_px = deadzone_px

        # Backward-compatible attributes
        self.min_alpha = 0.18
        self.max_alpha = 0.82
        self.base_speed_threshold = 40.0

        self.prev_x: float | None = None
        self.prev_y: float | None = None
        self.prev_edx: float = 0.0
        self.prev_edy: float = 0.0
        self.prev_time: float | None = None

    def configure(self, smoothing_level: float = 0.50, sniper_mode: bool = False, pre_click_damping: float = 0.0):
        """Map user smoothing slider (0.0 snappy .. 1.0 ultra-smooth) to One-Euro parameters."""
        s = max(0.0, min(1.0, float(smoothing_level)))
        d = max(0.0, min(1.0, float(pre_click_damping)))

        if sniper_mode:
            self.min_cutoff = 0.35
            self.beta = 2.2
            self.d_cutoff = 1.8
            self.deadzone_px = 4.0
        else:
            # Exponential curve feels linear to human perception across 0%..100% slider
            self.min_cutoff = 3.4 * ((0.45 / 3.4) ** s)       # 3.4 Hz -> 0.45 Hz
            self.beta = 28.0 * ((5.5 / 28.0) ** s)             # 28.0 -> 5.5
            self.d_cutoff = 2.8 - (0.8 * s)                    # 2.8 -> 2.0 Hz
            self.deadzone_px = 0.8 + (3.6 * s)                 # 0.8 px -> 4.4 px

        # Smoothly dampen micro-motion while middle finger rises toward a click
        if d > 0.0:
            self.min_cutoff *= (1.0 - 0.65 * d)
            self.beta *= (1.0 - 0.70 * d)
            self.deadzone_px += 2.5 * d

    def update(
        self,
        target_x: float,
        target_y: float,
        span_factor: float = 1.0,
        now: float | None = None,
    ) -> tuple[int, int]:
        if target_x is None or target_y is None or math.isnan(target_x) or math.isnan(target_y):
            return int(round(self.prev_x or 0.0)), int(round(self.prev_y or 0.0))

        if span_factor <= 0.0 or math.isnan(span_factor):
            span_factor = 1.0

        t = time.perf_counter() if now is None else float(now)

        if self.prev_x is None or self.prev_y is None or self.prev_time is None:
            self.prev_x = float(target_x)
            self.prev_y = float(target_y)
            self.prev_edx = 0.0
            self.prev_edy = 0.0
            self.prev_time = t
            return int(round(self.prev_x)), int(round(self.prev_y))

        raw_dt = t - self.prev_time
        self.prev_time = t

        # If tracking resumed after a long gap, reset derivative so velocity doesn't spike
        if raw_dt > 0.25:
            self.prev_edx = 0.0
            self.prev_edy = 0.0
        dt = max(1.0 / 240.0, min(raw_dt, 0.10))

        dx_raw = float(target_x) - self.prev_x
        dy_raw = float(target_y) - self.prev_y

        # Filtered velocity (derivative)
        vx = dx_raw / dt
        vy = dy_raw / dt
        a_d = _smoothing_factor(dt, self.d_cutoff)
        edx = self.prev_edx + a_d * (vx - self.prev_edx)
        edy = self.prev_edy + a_d * (vy - self.prev_edy)
        self.prev_edx = edx
        self.prev_edy = edy

        # Isotropic normalized speed (screen widths per second) so diagonal lines stay straight
        ref_span = 1920.0 * span_factor
        norm_speed = math.hypot(edx, edy) / ref_span
        cutoff = self.min_cutoff + self.beta * norm_speed
        alpha = _smoothing_factor(dt, cutoff)

        # Soft quadratic micro-jitter deadzone (eliminates stationary tremor without sticky feel)
        dist = math.hypot(dx_raw, dy_raw)
        dz = self.deadzone_px * max(1.0, span_factor * 0.85)
        if dz > 0.0 and dist < dz:
            ratio = dist / dz
            alpha *= (ratio * ratio)

        smooth_x = self.prev_x + alpha * dx_raw
        smooth_y = self.prev_y + alpha * dy_raw

        self.prev_x = smooth_x
        self.prev_y = smooth_y
        return int(round(smooth_x)), int(round(smooth_y))

    def reset(self):
        self.prev_x = None
        self.prev_y = None
        self.prev_edx = 0.0
        self.prev_edy = 0.0
        self.prev_time = None
