import math
from PIL import Image, ImageDraw
import customtkinter as ctk


def _hex_to_rgba(hex_color: str, alpha: int = 255) -> tuple[int, int, int, int]:
    h = hex_color.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), alpha)


def _new_neo_badge(fill_hex: str, size: int = 128):
    """Creates a crisp Neo-Brutalist square badge with hard offset black shadow and thick black border."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    ink = (17, 17, 17, 255)
    fill = _hex_to_rgba(fill_hex, 255)

    # Hard offset shadow (no blur)
    draw.rounded_rectangle([14, 14, size - 3, size - 3], radius=16, fill=ink)
    # Vivid Neo-Brutalist tile with thick black border
    draw.rounded_rectangle([5, 5, size - 13, size - 13], radius=16, fill=fill, outline=ink, width=6)
    return img, draw


def _capsule_layer(draw: ImageDraw.ImageDraw, x1, y1, x2, y2, r, color):
    """Draws a smooth rounded capsule between (x1, y1) and (x2, y2) with radius r."""
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    if length < 0.001:
        draw.ellipse([x1 - r, y1 - r, x1 + r, y1 + r], fill=color)
        return
    nx, ny = -dy / length * r, dx / length * r
    poly = [
        (x1 + nx, y1 + ny),
        (x2 + nx, y2 + ny),
        (x2 - nx, y2 - ny),
        (x1 - nx, y1 - ny),
    ]
    draw.polygon(poly, fill=color)
    draw.ellipse([x1 - r, y1 - r, x1 + r, y1 + r], fill=color)
    draw.ellipse([x2 - r, y2 - r, x2 + r, y2 + r], fill=color)


def _draw_outlined_capsule(draw, x1, y1, x2, y2, r, fill, ink=(17, 17, 17, 255), border=4):
    _capsule_layer(draw, x1, y1, x2, y2, r + border, ink)
    _capsule_layer(draw, x1, y1, x2, y2, r, fill)


def _draw_hand_pose(d: ImageDraw.ImageDraw, pose: str):
    """
    Draws bold, unmistakable Neo-Brutalist illustrated hand poses inside the 128x128 tile
    (usable inner tile area: [10..110, 10..110], center ~(60, 60)).
    """
    ink = (17, 17, 17, 255)
    hand = (255, 255, 255, 255)
    shade = (232, 236, 244, 255)
    spark = (17, 17, 17, 255)

    # Helper to draw standard palm base
    def palm_base(x1=36, y1=58, x2=84, y2=98):
        d.rounded_rectangle([x1 - 4, y1 - 4, x2 + 4, y2 + 4], radius=22, fill=ink)
        d.rounded_rectangle([x1, y1, x2, y2], radius=18, fill=hand)

    if pose == "cursor":
        # ☝️ INDEX FINGER UP (Pointing)
        # Extended tall index finger
        _draw_outlined_capsule(d, 46, 62, 46, 22, 7.5, hand, ink, 4)
        # Palm base
        palm_base(37, 56, 83, 98)
        # Re-blend index into palm cleanly
        _capsule_layer(d, 46, 64, 46, 23, 7.5, hand)
        # 3 Curled fingers (middle, ring, pinky)
        _draw_outlined_capsule(d, 59, 55, 59, 64, 6.5, shade, ink, 3.5)
        _draw_outlined_capsule(d, 70, 58, 70, 66, 6.0, shade, ink, 3.5)
        _draw_outlined_capsule(d, 80, 63, 80, 70, 5.5, shade, ink, 3.5)
        # Thumb tucked cleanly across lower-left palm
        _draw_outlined_capsule(d, 35, 82, 52, 71, 6.5, hand, ink, 3.5)

    elif pose == "click":
        # ✌️ INDEX + MIDDLE PINCHED TOGETHER (Click)
        _draw_outlined_capsule(d, 46, 67, 51, 30, 6.8, hand, ink, 4)
        _draw_outlined_capsule(d, 64, 67, 59, 30, 6.8, hand, ink, 4)
        palm_base(37, 61, 83, 100)
        _capsule_layer(d, 46, 69, 51, 31, 6.8, hand)
        _capsule_layer(d, 64, 69, 59, 31, 6.8, hand)
        d.line([(55, 30), (55, 60)], fill=ink, width=3)
        _draw_outlined_capsule(d, 72, 63, 72, 71, 5.8, shade, ink, 3.5)
        _draw_outlined_capsule(d, 81, 68, 81, 75, 5.2, shade, ink, 3.5)
        _draw_outlined_capsule(d, 35, 84, 50, 74, 6.2, hand, ink, 3.5)
        # Crisp click spark burst cleanly above touching tips
        d.line([(55, 14), (55, 21)], fill=spark, width=4)
        d.line([(40, 17), (45, 23)], fill=spark, width=4)
        d.line([(70, 17), (65, 23)], fill=spark, width=4)

    elif pose == "pause":
        # 🖐️ OPEN PALM (All 5 Fingers Extended & Fanned with crisp breathing room)
        _draw_outlined_capsule(d, 43, 79, 25, 58, 6.2, hand, ink, 4)
        _draw_outlined_capsule(d, 47, 65, 40, 31, 5.9, hand, ink, 4)
        _draw_outlined_capsule(d, 57, 63, 56, 25, 5.9, hand, ink, 4)
        _draw_outlined_capsule(d, 67, 64, 71, 29, 5.7, hand, ink, 4)
        _draw_outlined_capsule(d, 76, 68, 85, 40, 5.3, hand, ink, 4)
        palm_base(40, 61, 80, 98)
        _capsule_layer(d, 43, 79, 26, 59, 6.2, hand)
        _capsule_layer(d, 47, 67, 40, 32, 5.9, hand)
        _capsule_layer(d, 57, 65, 56, 26, 5.9, hand)
        _capsule_layer(d, 67, 66, 71, 30, 5.7, hand)
        _capsule_layer(d, 76, 70, 85, 41, 5.3, hand)
        d.line([(48, 59), (49, 65)], fill=ink, width=3)
        d.line([(61, 59), (61, 65)], fill=ink, width=3)
        d.line([(71, 61), (70, 67)], fill=ink, width=3)

    elif pose == "sniper":
        # 🤘 INDEX + PINKY UP (Sniper Mode)
        _draw_outlined_capsule(d, 41, 65, 38, 25, 6.6, hand, ink, 4)
        _draw_outlined_capsule(d, 79, 67, 84, 30, 5.8, hand, ink, 4)
        palm_base(36, 59, 84, 99)
        _capsule_layer(d, 41, 67, 38, 26, 6.6, hand)
        _capsule_layer(d, 79, 69, 84, 31, 5.8, hand)
        _draw_outlined_capsule(d, 54, 58, 54, 67, 6.2, shade, ink, 3.5)
        _draw_outlined_capsule(d, 66, 59, 66, 68, 6.0, shade, ink, 3.5)
        _draw_outlined_capsule(d, 37, 80, 61, 72, 6.2, hand, ink, 3.5)

    elif pose == "scroll":
        # ✌️ INDEX + MIDDLE APART (Open V-Sign + Clean Scroll Chevrons)
        _draw_outlined_capsule(d, 47, 65, 30, 25, 6.5, hand, ink, 4)
        _draw_outlined_capsule(d, 63, 65, 76, 25, 6.5, hand, ink, 4)
        palm_base(37, 59, 83, 99)
        _capsule_layer(d, 47, 67, 30, 26, 6.5, hand)
        _capsule_layer(d, 63, 67, 76, 26, 6.5, hand)
        _draw_outlined_capsule(d, 73, 62, 73, 70, 5.5, shade, ink, 3.5)
        _draw_outlined_capsule(d, 82, 67, 82, 74, 5.0, shade, ink, 3.5)
        _draw_outlined_capsule(d, 35, 82, 52, 73, 6.2, hand, ink, 3.5)
        # Crisp up/down scroll arrows centered cleanly in the V gap
        d.polygon([(53, 18), (46, 27), (60, 27)], fill=ink)
        d.polygon([(53, 45), (46, 36), (60, 36)], fill=ink)

    elif pose == "drag":
        # 👌 THUMB + INDEX PINCH HOLD (Clean OK Pinch Loop)
        # Relaxed middle/ring/pinky stacked on right side
        _draw_outlined_capsule(d, 65, 59, 71, 31, 5.8, shade, ink, 4)
        _draw_outlined_capsule(d, 74, 63, 83, 41, 5.4, shade, ink, 4)
        _draw_outlined_capsule(d, 81, 70, 90, 54, 5.0, shade, ink, 4)
        # Palm base
        palm_base(43, 57, 85, 97)
        # Curved Index arch to pinch tip (30, 50)
        _draw_outlined_capsule(d, 55, 58, 45, 34, 6.3, hand, ink, 4)
        _draw_outlined_capsule(d, 45, 34, 30, 48, 6.0, hand, ink, 4)
        # Curved Thumb arch to pinch tip (30, 55)
        _draw_outlined_capsule(d, 46, 80, 31, 66, 6.3, hand, ink, 4)
        _draw_outlined_capsule(d, 31, 66, 30, 55, 6.0, hand, ink, 4)
        # Seamless white palm fill blending cleanly into thumb & index bases
        d.rounded_rectangle([45, 59, 83, 95], radius=16, fill=hand)
        _capsule_layer(d, 55, 61, 46, 38, 6.0, hand)
        _capsule_layer(d, 47, 79, 34, 68, 6.0, hand)
        # Bold pinch contact dot
        d.ellipse([25, 47, 35, 57], fill=ink)

    elif pose == "right_click":
        # 3 FINGERS UP (Index + Middle + Ring Extended)
        _draw_outlined_capsule(d, 44, 63, 38, 25, 6.4, hand, ink, 4)
        _draw_outlined_capsule(d, 57, 61, 57, 19, 6.4, hand, ink, 4)
        _draw_outlined_capsule(d, 70, 63, 76, 25, 6.4, hand, ink, 4)
        palm_base(37, 58, 83, 98)
        _capsule_layer(d, 44, 65, 38, 26, 6.4, hand)
        _capsule_layer(d, 57, 63, 57, 20, 6.4, hand)
        _capsule_layer(d, 70, 65, 76, 26, 6.4, hand)
        # Pinky curled down on right
        _draw_outlined_capsule(d, 81, 65, 81, 73, 5.2, shade, ink, 3.5)
        # Thumb tucked in on left
        _draw_outlined_capsule(d, 35, 81, 51, 72, 6.2, hand, ink, 3.5)

    elif pose == "screenshot":
        # ✊ CLOSED FIST
        # Compact fist palm
        palm_base(33, 50, 87, 96)
        # 4 tightly curled fingers across top of fist
        _draw_outlined_capsule(d, 41, 41, 41, 56, 7.0, hand, ink, 4)
        _draw_outlined_capsule(d, 54, 38, 54, 55, 7.0, hand, ink, 4)
        _draw_outlined_capsule(d, 67, 40, 67, 56, 6.8, hand, ink, 4)
        _draw_outlined_capsule(d, 79, 44, 79, 58, 6.2, hand, ink, 4)
        # Thumb wrapped firmly horizontally across front of curled fingers
        _draw_outlined_capsule(d, 36, 70, 65, 63, 7.2, hand, ink, 4)


def make_icon(name: str, color: str, display_size: int = 34) -> ctk.CTkImage:
    S = 128
    img, d = _new_neo_badge(color, S)
    ink = (17, 17, 17, 255)
    white = (255, 255, 255, 255)
    cx, cy = 60, 60

    # Hand Pose Representations for Gesture List!
    hand_poses = {"cursor", "click", "pause", "sniper", "scroll", "drag", "right_click", "screenshot"}
    if name in hand_poses:
        _draw_hand_pose(d, name)

    elif name == "camera":
        # Viewfinder 4 corner brackets + camera lens (for offline camera & calibrate)
        c = 20
        d.line([(24, 24), (24 + c, 24)], fill=ink, width=8)
        d.line([(24, 24), (24, 24 + c)], fill=ink, width=8)
        d.line([(96, 24), (96 - c, 24)], fill=ink, width=8)
        d.line([(96, 24), (96, 24 + c)], fill=ink, width=8)
        d.line([(24, 96), (24 + c, 96)], fill=ink, width=8)
        d.line([(24, 96), (24, 96 - c)], fill=ink, width=8)
        d.line([(96, 96), (96 - c, 96)], fill=ink, width=8)
        d.line([(96, 96), (96, 96 - c)], fill=ink, width=8)
        d.ellipse([44, 44, 76, 76], fill=white, outline=ink, width=6)
        d.ellipse([54, 54, 66, 66], fill=ink)

    elif name == "calibrate":
        d.ellipse([30, 30, 90, 90], outline=ink, width=7)
        d.line([(cx, 16), (cx, 38)], fill=ink, width=7)
        d.line([(cx, 82), (cx, 104)], fill=ink, width=7)
        d.line([(16, cy), (38, cy)], fill=ink, width=7)
        d.line([(82, cy), (104, cy)], fill=ink, width=7)
        d.ellipse([53, 53, 67, 67], fill=ink)

    elif name == "hud":
        d.rounded_rectangle([22, 28, 98, 92], radius=8, fill=white, outline=ink, width=6)
        d.rounded_rectangle([50, 56, 90, 82], radius=5, fill=ink)

    elif name == "mirror":
        d.line([(cx, 22), (cx, 98)], fill=ink, width=6)
        d.polygon([(50, 34), (50, 86), (24, 60)], fill=ink)
        d.polygon([(70, 34), (70, 86), (96, 60)], fill=white, outline=ink, width=6)

    elif name == "audio":
        d.polygon([(24, 48), (42, 48), (62, 30), (62, 90), (42, 72), (24, 72)], fill=ink)
        d.arc([62, 42, 84, 78], start=300, end=60, fill=ink, width=6)
        d.arc([70, 30, 100, 90], start=300, end=60, fill=ink, width=6)

    elif name == "skeleton":
        pts = [(60, 92), (38, 64), (32, 34), (60, 26), (88, 38)]
        d.line([pts[0], pts[1], pts[2]], fill=ink, width=6)
        d.line([pts[0], pts[3]], fill=ink, width=6)
        d.line([pts[0], pts[4]], fill=ink, width=6)
        for px, py in pts:
            d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=white, outline=ink, width=5)

    elif name == "box":
        c = 20
        d.line([(24, 24), (24 + c, 24)], fill=ink, width=8)
        d.line([(24, 24), (24, 24 + c)], fill=ink, width=8)
        d.line([(96, 24), (96 - c, 24)], fill=ink, width=8)
        d.line([(96, 24), (96, 24 + c)], fill=ink, width=8)
        d.line([(24, 96), (24 + c, 96)], fill=ink, width=8)
        d.line([(24, 96), (24, 96 - c)], fill=ink, width=8)
        d.line([(96, 96), (96 - c, 96)], fill=ink, width=8)
        d.line([(96, 96), (96, 96 - c)], fill=ink, width=8)

    elif name == "telemetry":
        d.line([(18, 64), (38, 64), (50, 30), (66, 90), (80, 56), (102, 56)], fill=ink, width=8, joint="curve")

    elif name == "tracker":
        d.ellipse([28, 28, 92, 92], outline=ink, width=8)
        d.ellipse([48, 48, 72, 72], fill=ink)

    elif name == "palette":
        d.ellipse([24, 24, 96, 96], fill=white, outline=ink, width=6)
        d.ellipse([38, 40, 52, 54], fill=ink)
        d.ellipse([64, 34, 78, 48], fill=ink)
        d.ellipse([66, 64, 80, 78], fill=ink)

    resized = img.resize((display_size, display_size), Image.Resampling.LANCZOS)
    return ctk.CTkImage(light_image=resized, dark_image=resized, size=(display_size, display_size))
