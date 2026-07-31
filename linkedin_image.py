"""Premium LinkedIn infographics (1080x1350) — dense, designed, no author name.

Goal: look like a polished Canva/Figma Health IT post — not a sparse diagram.
"""

from __future__ import annotations

import hashlib
import math
import random
from pathlib import Path
from typing import Any

WIDTH = 1080
HEIGHT = 1350

# Premium palettes inspired by high-performing Health IT LinkedIn posts
PALETTES = {
    "ocean": {
        "bg": (236, 244, 255),
        "bg2": (214, 232, 255),
        "surface": (255, 255, 255),
        "ink": (15, 23, 42),
        "muted": (71, 85, 105),
        "accent": (37, 99, 235),
        "accent2": (14, 165, 233),
        "accent3": (99, 102, 241),
        "header": (30, 64, 175),
        "header2": (37, 99, 235),
        "chip": (219, 234, 254),
        "good": (22, 163, 74),
        "bad": (71, 85, 105),
        "line": (191, 219, 254),
    },
    "teal": {
        "bg": (240, 253, 250),
        "bg2": (204, 251, 241),
        "surface": (255, 255, 255),
        "ink": (19, 78, 74),
        "muted": (45, 106, 100),
        "accent": (13, 148, 136),
        "accent2": (20, 184, 166),
        "accent3": (45, 212, 191),
        "header": (15, 118, 110),
        "header2": (13, 148, 136),
        "chip": (204, 251, 241),
        "good": (16, 185, 129),
        "bad": (100, 116, 139),
        "line": (153, 246, 228),
    },
    "violet": {
        "bg": (245, 243, 255),
        "bg2": (237, 233, 254),
        "surface": (255, 255, 255),
        "ink": (46, 16, 101),
        "muted": (76, 29, 149),
        "accent": (124, 58, 237),
        "accent2": (139, 92, 246),
        "accent3": (167, 139, 250),
        "header": (91, 33, 182),
        "header2": (124, 58, 237),
        "chip": (237, 233, 254),
        "good": (16, 185, 129),
        "bad": (100, 116, 139),
        "line": (221, 214, 254),
    },
    "sunset": {
        "bg": (255, 247, 237),
        "bg2": (255, 237, 213),
        "surface": (255, 255, 255),
        "ink": (67, 20, 7),
        "muted": (154, 52, 18),
        "accent": (234, 88, 12),
        "accent2": (249, 115, 22),
        "accent3": (251, 146, 60),
        "header": (194, 65, 12),
        "header2": (234, 88, 12),
        "chip": (255, 237, 213),
        "good": (22, 163, 74),
        "bad": (100, 116, 139),
        "line": (254, 215, 170),
    },
    "midnight": {
        "bg": (2, 6, 23),
        "bg2": (15, 23, 42),
        "surface": (30, 41, 59),
        "ink": (248, 250, 252),
        "muted": (148, 163, 184),
        "accent": (52, 211, 153),
        "accent2": (34, 211, 238),
        "accent3": (167, 139, 250),
        "header": (15, 23, 42),
        "header2": (30, 41, 59),
        "chip": (51, 65, 85),
        "good": (52, 211, 153),
        "bad": (148, 163, 184),
        "line": (51, 65, 85),
    },
    "split": {
        "bg": (248, 250, 252),
        "bg2": (241, 245, 249),
        "surface": (255, 255, 255),
        "ink": (255, 255, 255),
        "muted": (226, 232, 240),
        "accent": (255, 255, 255),
        "accent2": (255, 255, 255),
        "accent3": (255, 255, 255),
        "header": (15, 23, 42),
        "header2": (22, 163, 74),
        "chip": (255, 255, 255),
        "good": (22, 163, 74),
        "bad": (71, 85, 105),
        "line": (255, 255, 255),
    },
}


def _fonts(scale: int = 1) -> dict[str, Any]:
    from PIL import ImageFont

    bold_paths = [
        r"C:\Windows\Fonts\segoeuib.ttf",
        r"C:\Windows\Fonts\arialbd.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    reg_paths = [
        r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    bold = next((p for p in bold_paths if Path(p).exists()), None)
    reg = next((p for p in reg_paths if Path(p).exists()), None)
    s = max(scale, 1)
    if not bold or not reg:
        d = ImageFont.load_default()
        print("[image] WARNING: missing TTF fonts")
        return {k: d for k in ("display", "h1", "h2", "h3", "body", "small", "tiny")}
    return {
        "display": ImageFont.truetype(bold, 64 * s),
        "h1": ImageFont.truetype(bold, 48 * s),
        "h2": ImageFont.truetype(bold, 34 * s),
        "h3": ImageFont.truetype(bold, 26 * s),
        "body": ImageFont.truetype(reg, 24 * s),
        "small": ImageFont.truetype(reg, 20 * s),
        "tiny": ImageFont.truetype(reg, 16 * s),
    }


def _seed(post: dict[str, Any]) -> int:
    key = f"{post.get('topic')}|{post.get('image_title')}|{post.get('hook')}|{post.get('image_layout')}"
    return int(hashlib.md5(key.encode()).hexdigest()[:8], 16)


def _palette(post: dict[str, Any]) -> dict[str, tuple[int, int, int]]:
    layout = (post.get("image_layout") or "").lower()
    theme = (post.get("accent_theme") or "").lower()
    mapping = {
        "green_split": "split",
        "blue": "ocean",
        "teal": "teal",
        "purple": "violet",
        "orange": "sunset",
        "dark_green": "midnight",
        "navy": "midnight",
    }
    name = mapping.get(theme)
    if layout == "split_compare":
        name = "split"
    elif layout == "dark_tech":
        name = "midnight"
    if not name:
        names = ["ocean", "teal", "violet", "sunset", "midnight"]
        name = names[_seed(post) % len(names)]
    return PALETTES[name]


def _wrap(text: str, font: Any, max_w: int, draw: Any) -> list[str]:
    words = (text or "").split()
    if not words:
        return []
    lines: list[str] = []
    cur = words[0]
    for w in words[1:]:
        trial = f"{cur} {w}"
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def _title(post: dict[str, Any]) -> str:
    t = (post.get("image_title") or post.get("hook") or post.get("topic") or "Healthcare Interoperability").strip()
    words = t.split()
    return " ".join(words[:9]) if len(words) > 9 else t


def _subtitle(post: dict[str, Any]) -> str:
    return (post.get("image_subtitle") or "").strip()


def _gradient(img: Any, c1: tuple[int, int, int], c2: tuple[int, int, int], vertical: bool = True) -> None:
    from PIL import ImageDraw

    draw = ImageDraw.Draw(img)
    steps = HEIGHT if vertical else WIDTH
    for i in range(steps):
        t = i / max(steps - 1, 1)
        r = int(c1[0] + (c2[0] - c1[0]) * t)
        g = int(c1[1] + (c2[1] - c1[1]) * t)
        b = int(c1[2] + (c2[2] - c1[2]) * t)
        if vertical:
            draw.line([(0, i), (WIDTH, i)], fill=(r, g, b))
        else:
            draw.line([(i, 0), (i, HEIGHT)], fill=(r, g, b))


def _soft_blob(base: Any, xy: tuple[int, int], radius: int, color: tuple[int, int, int], alpha: int = 50) -> Any:
    from PIL import Image, ImageDraw, ImageFilter

    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    x, y = xy
    d.ellipse([x - radius, y - radius, x + radius, y + radius], fill=(*color, alpha))
    overlay = overlay.filter(ImageFilter.GaussianBlur(radius // 3))
    return Image.alpha_composite(base.convert("RGBA"), overlay)


def _card(base: Any, box: tuple[int, int, int, int], fill: tuple[int, int, int], radius: int = 28, shadow: bool = True) -> Any:
    from PIL import Image, ImageDraw, ImageFilter

    img = base.convert("RGBA")
    if shadow:
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(sh)
        sd.rounded_rectangle(
            [box[0] + 6, box[1] + 10, box[2] + 6, box[3] + 10],
            radius=radius,
            fill=(15, 23, 42, 45),
        )
        sh = sh.filter(ImageFilter.GaussianBlur(14))
        img = Image.alpha_composite(img, sh)
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.rounded_rectangle(list(box), radius=radius, fill=(*fill, 255))
    return Image.alpha_composite(img, layer)


def _pill(draw: Any, xy: tuple[int, int], text: str, font: Any, bg: tuple[int, int, int], fg: tuple[int, int, int]) -> int:
    pad_x, pad_y = 18, 10
    tw = draw.textlength(text, font=font)
    x, y = xy
    box = [x, y, x + tw + pad_x * 2, y + 34 + pad_y]
    draw.rounded_rectangle(box, radius=20, fill=bg)
    draw.text((x + pad_x, y + pad_y - 1), text, font=font, fill=fg)
    return int(box[2])


def _icon(draw: Any, cx: int, cy: int, kind: str, color: tuple[int, int, int], size: int = 42) -> None:
    s = size
    white = (255, 255, 255)
    draw.ellipse([cx - s, cy - s, cx + s, cy + s], fill=color)
    if kind == "doc":
        draw.rounded_rectangle([cx - 16, cy - 20, cx + 16, cy + 20], radius=4, fill=white)
        draw.line([(cx - 8, cy - 8), (cx + 8, cy - 8)], fill=color, width=3)
        draw.line([(cx - 8, cy + 2), (cx + 8, cy + 2)], fill=color, width=3)
        draw.line([(cx - 8, cy + 12), (cx + 4, cy + 12)], fill=color, width=3)
    elif kind == "api":
        draw.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], outline=white, width=4)
        draw.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=white)
        for ang in (45, 135, 225, 315):
            rad = math.radians(ang)
            draw.line(
                [(cx + int(18 * math.cos(rad)), cy + int(18 * math.sin(rad))),
                 (cx + int(28 * math.cos(rad)), cy + int(28 * math.sin(rad)))],
                fill=white,
                width=4,
            )
    elif kind == "app":
        draw.rounded_rectangle([cx - 18, cy - 22, cx + 18, cy + 22], radius=6, outline=white, width=4)
        draw.ellipse([cx - 5, cy + 12, cx + 5, cy + 18], fill=white)
    elif kind == "chain":
        draw.arc([cx - 22, cy - 12, cx - 2, cy + 12], 0, 360, fill=white, width=4)
        draw.arc([cx + 2, cy - 12, cx + 22, cy + 12], 0, 360, fill=white, width=4)
    elif kind == "rocket":
        draw.polygon([(cx, cy - 22), (cx + 16, cy + 14), (cx - 16, cy + 14)], fill=white)
        draw.ellipse([cx - 5, cy - 6, cx + 5, cy + 4], fill=color)
    elif kind == "server":
        draw.rounded_rectangle([cx - 18, cy - 20, cx + 18, cy + 20], radius=4, outline=white, width=3)
        draw.line([(cx - 10, cy - 6), (cx + 10, cy - 6)], fill=white, width=3)
        draw.line([(cx - 10, cy + 6), (cx + 10, cy + 6)], fill=white, width=3)
    elif kind == "cloud":
        draw.ellipse([cx - 22, cy - 6, cx + 4, cy + 18], fill=white)
        draw.ellipse([cx - 8, cy - 16, cx + 22, cy + 12], fill=white)
    elif kind == "check":
        draw.line([(cx - 14, cy), (cx - 2, cy + 14), (cx + 16, cy - 14)], fill=white, width=5)
    elif kind == "shield":
        draw.polygon(
            [(cx, cy - 22), (cx + 18, cy - 12), (cx + 14, cy + 14), (cx, cy + 22), (cx - 14, cy + 14), (cx - 18, cy - 12)],
            outline=white,
            width=3,
        )
        draw.line([(cx - 8, cy), (cx - 1, cy + 8), (cx + 10, cy - 10)], fill=white, width=3)
    elif kind == "people":
        draw.ellipse([cx - 8, cy - 18, cx + 8, cy - 2], fill=white)
        draw.ellipse([cx - 18, cy + 2, cx + 18, cy + 22], fill=white)
    else:
        draw.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill=white)


def _decor_network(base: Any, pal: dict[str, Any], seed: int, alpha: int = 70) -> Any:
    from PIL import Image, ImageDraw

    rng = random.Random(seed)
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    nodes = [(rng.randint(40, WIDTH - 40), rng.randint(40, HEIGHT - 40)) for _ in range(40)]
    accent = (*pal["accent"], alpha)
    line = (*pal["line"], max(30, alpha - 20))
    for i, (x, y) in enumerate(nodes):
        r = 4 if i % 2 else 6
        d.ellipse([x - r, y - r, x + r, y + r], fill=accent)
        if i:
            px, py = nodes[i - 1]
            if abs(px - x) + abs(py - y) < 420:
                d.line([(px, py), (x, y)], fill=line, width=2)
    for _ in range(5):
        cx, cy = rng.randint(80, WIDTH - 80), rng.randint(80, HEIGHT - 80)
        rad = rng.randint(60, 160)
        d.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], outline=(*pal["accent2"], 40), width=2)
    return Image.alpha_composite(base.convert("RGBA"), overlay)


def _footer_bar(draw: Any, fonts: dict[str, Any], pal: dict[str, Any], text: str = "#FHIR  ·  #CMS  ·  #Interoperability  ·  #HealthIT") -> None:
    draw.rectangle([0, HEIGHT - 70, WIDTH, HEIGHT], fill=pal["header"])
    tw = draw.textlength(text, font=fonts["small"])
    draw.text(((WIDTH - tw) / 2, HEIGHT - 48), text, font=fonts["small"], fill=(255, 255, 255))


def _layout_name(post: dict[str, Any]) -> str:
    layout = (post.get("image_layout") or "").strip().lower()
    allowed = {"split_compare", "title_network", "before_after", "key_points", "workflow", "dark_tech"}
    if layout in allowed:
        return layout
    return ["key_points", "before_after", "workflow", "title_network", "dark_tech", "split_compare"][_seed(post) % 6]


# ---------- LAYOUTS ----------

def _draw_split_compare(base: Any, fonts: dict[str, Any], post: dict[str, Any], pal: dict[str, Any]) -> Any:
    from PIL import Image, ImageDraw

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    mid = WIDTH // 2
    d.rectangle([0, 0, mid, HEIGHT], fill=pal["bad"])
    d.rectangle([mid, 0, WIDTH, HEIGHT], fill=pal["good"])

    # top banner
    d.rectangle([0, 0, WIDTH, 160], fill=(15, 23, 42))
    title = _title(post)
    y = 36
    for line in _wrap(title, fonts["h1"], WIDTH - 80, d)[:2]:
        tw = d.textlength(line, font=fonts["h1"])
        d.text(((WIDTH - tw) / 2, y), line, font=fonts["h1"], fill=(255, 255, 255))
        y += 52

    left_label = post.get("left_label") or "Before"
    right_label = post.get("right_label") or "After"
    left_points = list(post.get("left_points") or ["Fragile", "Costly", "Hard to scale"])[:3]
    right_points = list(post.get("right_points") or ["Reusable", "Faster", "Product-ready"])[:3]

    _icon(d, mid // 2, 320, "chain", (51, 65, 85), 52)
    _icon(d, mid + mid // 2, 320, "rocket", (21, 128, 61), 52)

    for label, cx, points, kind_bg in (
        (left_label, mid // 2, left_points, (51, 65, 85)),
        (right_label, mid + mid // 2, right_points, (21, 128, 61)),
    ):
        y = 420
        for line in _wrap(str(label), fonts["h2"], mid - 60, d)[:3]:
            tw = d.textlength(line, font=fonts["h2"])
            d.text((cx - tw / 2, y), line, font=fonts["h2"], fill=(255, 255, 255))
            y += 44
        y += 24
        for p in points:
            pw = mid - 80
            bx0 = cx - pw // 2
            d.rounded_rectangle([bx0, y, bx0 + pw, y + 70], radius=18, fill=(255, 255, 255))
            for j, pl in enumerate(_wrap(str(p), fonts["body"], pw - 40, d)[:2]):
                tw = d.textlength(pl, font=fonts["body"])
                d.text((cx - tw / 2, y + 18 + j * 26), pl, font=fonts["body"], fill=(15, 23, 42))
            y += 88

    d.rectangle([0, HEIGHT - 70, WIDTH, HEIGHT], fill=(15, 23, 42))
    tag = "#FHIR  ·  #Interoperability  ·  #HealthIT"
    tw = d.textlength(tag, font=fonts["small"])
    d.text(((WIDTH - tw) / 2, HEIGHT - 48), tag, font=fonts["small"], fill=(255, 255, 255))
    return img


def _draw_title_network(base: Any, fonts: dict[str, Any], post: dict[str, Any], pal: dict[str, Any]) -> Any:
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (WIDTH, HEIGHT))
    _gradient(img, pal["bg"], pal["bg2"])
    img = _decor_network(img, pal, _seed(post), 90)
    img = _soft_blob(img, (180, 220), 220, pal["accent2"], 40)
    img = _soft_blob(img, (900, 1100), 260, pal["accent3"], 35)

    badges = list(post.get("badge_labels") or ["FHIR", "CMS", "API", "Data"])[:4]
    positions = [(48, 70), (780, 90), (60, 1120), (760, 1100)]
    for (x, y), label in zip(positions, badges):
        img = _card(img, (x, y, x + 240, y + 100), pal["surface"], radius=22)
    d = ImageDraw.Draw(img)
    for (x, y), label in zip(positions, badges):
        tw = d.textlength(str(label)[:16], font=fonts["h3"])
        d.text((x + 120 - tw / 2, y + 32), str(label)[:16], font=fonts["h3"], fill=pal["accent"])

    # Hero center card
    img = _card(img, (70, 360, WIDTH - 70, 980), pal["surface"], radius=36)
    d = ImageDraw.Draw(img)
    _pill(d, (110, 420), "HEALTH IT INSIGHT", fonts["tiny"], pal["chip"], pal["accent"])

    title = _title(post)
    y = 500
    for line in _wrap(title, fonts["display"], WIDTH - 220, d)[:4]:
        d.text((110, y), line, font=fonts["display"], fill=pal["ink"])
        y += 78

    # accent underline
    d.rounded_rectangle([110, y + 10, 250, y + 22], radius=6, fill=pal["accent"])

    sub = _subtitle(post)
    if sub:
        y += 50
        for line in _wrap(sub, fonts["body"], WIDTH - 240, d)[:3]:
            d.text((110, y), line, font=fonts["body"], fill=pal["muted"])
            y += 34

    _footer_bar(d, fonts, pal)
    return img


def _draw_before_after(base: Any, fonts: dict[str, Any], post: dict[str, Any], pal: dict[str, Any]) -> Any:
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (WIDTH, HEIGHT))
    _gradient(img, pal["bg"], pal["bg2"])
    img = _soft_blob(img, (900, 200), 280, pal["accent2"], 45)

    # Header card
    img = _card(img, (40, 40, WIDTH - 40, 320), pal["header"], radius=32, shadow=True)
    d = ImageDraw.Draw(img)
    _pill(d, (80, 80), "MODERNISATION PATH", fonts["tiny"], (255, 255, 255), pal["header"])
    title = _title(post)
    y = 140
    for line in _wrap(title, fonts["display"], WIDTH - 180, d)[:2]:
        d.text((80, y), line, font=fonts["display"], fill=(255, 255, 255))
        y += 72
    sub = _subtitle(post)
    if sub:
        d.text((80, 260), sub[:70], font=fonts["body"], fill=(226, 232, 240))

    steps = list(post.get("steps") or ["Before", "Standard", "After"])[:3]
    while len(steps) < 3:
        steps.append("Next")
    kinds = ["server", "api", "app"]
    colors = [pal["bad"], pal["accent"], pal["good"]]
    labels_top = ["BEFORE", "BRIDGE", "AFTER"]
    card_w = 300
    gap = 30
    total = 3 * card_w + 2 * gap
    x0 = (WIDTH - total) // 2
    top = 400

    for i, step in enumerate(steps):
        x = x0 + i * (card_w + gap)
        img = _card(img, (x, top, x + card_w, top + 620), pal["surface"], radius=28)
    d = ImageDraw.Draw(img)

    for i, step in enumerate(steps):
        x = x0 + i * (card_w + gap)
        cx = x + card_w // 2
        # top color strip
        d.rounded_rectangle([x, top, x + card_w, top + 18], radius=8, fill=colors[i])
        _icon(d, cx, top + 120, kinds[i], colors[i], 48)
        tw = d.textlength(labels_top[i], font=fonts["tiny"])
        d.text((cx - tw / 2, top + 200), labels_top[i], font=fonts["tiny"], fill=colors[i])
        y = top + 260
        for line in _wrap(str(step), fonts["h3"], card_w - 40, d)[:5]:
            tw = d.textlength(line, font=fonts["h3"])
            d.text((cx - tw / 2, y), line, font=fonts["h3"], fill=pal["ink"])
            y += 40
        if i < 2:
            ax = x + card_w + 4
            ay = top + 300
            d.polygon([(ax, ay), (ax + gap - 8, ay + 12), (ax, ay + 24)], fill=pal["accent"])

    # Bottom insight banner — fills empty space for LinkedIn density
    banner_top = top + 660
    img = _card(img, (40, banner_top, WIDTH - 40, HEIGHT - 100), pal["surface"], radius=28)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([40, banner_top, 70, HEIGHT - 100], radius=12, fill=pal["accent"])
    d.text((100, banner_top + 40), "WHY THIS MATTERS", font=fonts["tiny"], fill=pal["accent"])
    insight = _subtitle(post) or "Standards open the door. Product and data quality decide who walks through."
    ty = banner_top + 90
    for line in _wrap(insight, fonts["h2"], WIDTH - 200, d)[:3]:
        d.text((100, ty), line, font=fonts["h2"], fill=pal["ink"])
        ty += 48
    # three mini stats/chips
    chips = list(post.get("badge_labels") or ["FHIR", "Member apps", "Data quality"])[:3]
    cx0 = 100
    for chip in chips:
        cx0 = _pill(d, (cx0, ty + 20), str(chip)[:22], fonts["small"], pal["chip"], pal["accent"]) + 16

    _footer_bar(d, fonts, pal)
    return img


def _draw_key_points(base: Any, fonts: dict[str, Any], post: dict[str, Any], pal: dict[str, Any]) -> Any:
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (WIDTH, HEIGHT))
    _gradient(img, pal["bg"], pal["bg2"])
    img = _soft_blob(img, (980, 180), 240, pal["accent3"], 40)

    img = _card(img, (36, 36, WIDTH - 36, 300), pal["header"], radius=32)
    d = ImageDraw.Draw(img)
    badges = list(post.get("badge_labels") or ["FHIR", "CMS"])[:2]
    bx = 80
    for b in badges:
        bx = _pill(d, (bx, 70), str(b).upper()[:18], fonts["tiny"], (255, 255, 255), pal["header"]) + 12
    title = _title(post)
    y = 130
    for line in _wrap(title, fonts["display"], WIDTH - 160, d)[:2]:
        d.text((80, y), line, font=fonts["display"], fill=(255, 255, 255))
        y += 70
    sub = _subtitle(post)
    if sub:
        d.text((80, 250), sub[:72], font=fonts["body"], fill=(226, 232, 240))

    bullets = list(post.get("bullets") or post.get("steps") or ["Insight one", "Insight two", "Insight three", "Insight four"])[:4]
    colors = [pal["good"], pal["accent2"], pal["accent"], (239, 68, 68)]
    icon_kinds = ["shield", "api", "people", "check"]
    top = 360
    card_h = 180
    for i, bullet in enumerate(bullets):
        y0 = top + i * (card_h + 24)
        img = _card(img, (36, y0, WIDTH - 36, y0 + card_h), pal["surface"], radius=26)
    d = ImageDraw.Draw(img)
    for i, bullet in enumerate(bullets):
        y0 = top + i * (card_h + 24)
        # left accent
        d.rounded_rectangle([36, y0, 56, y0 + card_h], radius=10, fill=colors[i % 4])
        _icon(d, 120, y0 + card_h // 2, icon_kinds[i % 4], colors[i % 4], 36)
        # number
        d.text((180, y0 + 36), f"{i + 1:02d}", font=fonts["h2"], fill=colors[i % 4])
        ty = y0 + 90
        for line in _wrap(str(bullet), fonts["h3"], WIDTH - 260, d)[:2]:
            d.text((180, ty), line, font=fonts["h3"], fill=pal["ink"])
            ty += 36

    _footer_bar(d, fonts, pal)
    return img


def _draw_workflow(base: Any, fonts: dict[str, Any], post: dict[str, Any], pal: dict[str, Any]) -> Any:
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (WIDTH, HEIGHT))
    _gradient(img, pal["bg"], pal["bg2"])

    img = _card(img, (36, 36, WIDTH - 36, 280), pal["header"], radius=32)
    d = ImageDraw.Draw(img)
    _pill(d, (80, 70), "WORKFLOW", fonts["tiny"], (255, 255, 255), pal["header"])
    title = _title(post)
    y = 120
    for line in _wrap(title, fonts["h1"], WIDTH - 160, d)[:2]:
        d.text((80, y), line, font=fonts["h1"], fill=(255, 255, 255))
        y += 56
    sub = _subtitle(post)
    if sub:
        d.text((80, 230), sub[:70], font=fonts["small"], fill=(226, 232, 240))

    steps = list(post.get("steps") or ["Start", "Exchange", "Validate", "Decide", "Deliver"])[:5]
    n = len(steps)
    # Vertical timeline for premium look (fills tall canvas)
    top = 360
    for i, step in enumerate(steps):
        y0 = top + i * 160
        img = _card(img, (120, y0, WIDTH - 48, y0 + 130), pal["surface"], radius=24)
    d = ImageDraw.Draw(img)
    # timeline spine
    d.line([(78, top + 20), (78, top + (n - 1) * 160 + 100)], fill=pal["accent"], width=6)
    for i, step in enumerate(steps):
        y0 = top + i * 160
        cy = y0 + 65
        d.ellipse([54, cy - 24, 102, cy + 24], fill=pal["accent"])
        tw = d.textlength(str(i + 1), font=fonts["h3"])
        d.text((78 - tw / 2, cy - 14), str(i + 1), font=fonts["h3"], fill=(255, 255, 255))
        d.text((160, y0 + 28), f"STEP {i + 1}", font=fonts["tiny"], fill=pal["accent"])
        ty = y0 + 58
        for line in _wrap(str(step), fonts["h3"], WIDTH - 240, d)[:2]:
            d.text((160, ty), line, font=fonts["h3"], fill=pal["ink"])
            ty += 34

    _footer_bar(d, fonts, pal)
    return img


def _draw_dark_tech(base: Any, fonts: dict[str, Any], post: dict[str, Any], pal: dict[str, Any]) -> Any:
    from PIL import Image, ImageDraw

    pal = PALETTES["midnight"]
    img = Image.new("RGB", (WIDTH, HEIGHT))
    _gradient(img, pal["bg"], pal["bg2"])
    img = _decor_network(img, pal, _seed(post), 110)
    img = _soft_blob(img, (900, 300), 300, pal["accent"], 35)

    d = ImageDraw.Draw(img)
    _pill(d, (48, 48), "TECHNICAL ANATOMY", fonts["tiny"], pal["chip"], pal["accent"])
    title = _title(post)
    y = 110
    for line in _wrap(title, fonts["h1"], WIDTH - 100, d)[:3]:
        d.text((48, y), line, font=fonts["h1"], fill=pal["accent"])
        y += 58
    sub = _subtitle(post)
    if sub:
        for line in _wrap(sub, fonts["body"], WIDTH - 100, d)[:2]:
            d.text((48, y + 8), line, font=fonts["body"], fill=pal["muted"])
            y += 32

    bullets = list(post.get("bullets") or ["Component one", "Component two", "Component three", "Component four"])[:5]
    y0 = y + 40
    for i, b in enumerate(bullets):
        yy = y0 + i * 130
        if yy + 110 > HEIGHT - 100:
            break
        img = _card(img, (48, yy, 680, yy + 110), pal["surface"], radius=20, shadow=False)
    d = ImageDraw.Draw(img)
    for i, b in enumerate(bullets):
        yy = y0 + i * 130
        if yy + 110 > HEIGHT - 100:
            break
        d.rounded_rectangle([48, yy, 680, yy + 110], radius=20, outline=pal["accent"], width=2)
        d.ellipse([72, yy + 35, 112, yy + 75], fill=pal["accent"])
        tw = d.textlength(str(i + 1), font=fonts["h3"])
        d.text((92 - tw / 2, yy + 42), str(i + 1), font=fonts["h3"], fill=pal["bg"])
        ty = yy + 30
        for line in _wrap(str(b), fonts["body"], 520, d)[:2]:
            d.text((140, ty), line, font=fonts["body"], fill=pal["ink"])
            ty += 30

    # Hub
    cx, cy = 880, 780
    d.ellipse([cx - 120, cy - 120, cx + 120, cy + 120], outline=pal["accent"], width=4)
    d.ellipse([cx - 80, cy - 80, cx + 80, cy + 80], outline=pal["accent2"], width=2)
    hub = str(post.get("hub_label") or "FHIR")[:8]
    tw = d.textlength(hub, font=fonts["h2"])
    d.text((cx - tw / 2, cy - 20), hub, font=fonts["h2"], fill=pal["accent"])
    for ang in range(0, 360, 72):
        rad = math.radians(ang - 90)
        x = cx + int(170 * math.cos(rad))
        y = cy + int(170 * math.sin(rad))
        d.line([(cx, cy), (x, y)], fill=pal["accent2"], width=3)
        d.ellipse([x - 16, y - 16, x + 16, y + 16], fill=pal["accent2"])

    _footer_bar(d, fonts, pal)
    return img


LAYOUTS = {
    "split_compare": _draw_split_compare,
    "title_network": _draw_title_network,
    "before_after": _draw_before_after,
    "key_points": _draw_key_points,
    "workflow": _draw_workflow,
    "dark_tech": _draw_dark_tech,
}


def _enrich(post: dict[str, Any]) -> dict[str, Any]:
    p = dict(post)
    p["image_layout"] = _layout_name(p)
    p.setdefault("image_title", _title(p))
    if not p.get("badge_labels"):
        t = (p.get("topic") or "").lower()
        if "patient" in t:
            p["badge_labels"] = ["Patient Access", "FHIR", "Member", "Apps"]
        elif "pas" in t:
            p["badge_labels"] = ["PAS", "Claim", "Coverage", "Actors"]
        elif "uscdi" in t or "us core" in t:
            p["badge_labels"] = ["USCDI", "US Core", "Must Support", "Apps"]
        else:
            p["badge_labels"] = ["FHIR", "CMS", "API", "Interop"]
    return p


def create_post_image(post: dict[str, Any], out_path: Path) -> Path:
    from PIL import Image

    global WIDTH, HEIGHT

    post = _enrich(post)
    layout = post["image_layout"]
    pal = _palette(post)

    # 2× supersample for crisp LinkedIn text, then downscale
    scale = 2
    out_w, out_h = 1080, 1350
    WIDTH, HEIGHT = out_w * scale, out_h * scale
    fonts = _fonts(scale=scale)

    base = Image.new("RGB", (WIDTH, HEIGHT), pal["bg"])
    img = LAYOUTS.get(layout, _draw_key_points)(base, fonts, post, pal)
    if img.mode != "RGB":
        img = img.convert("RGB")
    img = img.resize((out_w, out_h), Image.Resampling.LANCZOS)

    WIDTH, HEIGHT = out_w, out_h
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, format="PNG", compress_level=4)
    print(f"[image] Premium '{layout}' saved: {out_path.name} ({out_w}x{out_h})")
    return out_path


def image_path_for_draft(draft_md: Path) -> Path:
    return draft_md.with_suffix(".png")
