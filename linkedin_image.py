"""Premium LinkedIn HUD / HealthTech visuals (1080x1350).

10+ distinct layouts + color themes so every post image looks unique.
No photo/skeleton backgrounds. No author name on the image.
"""

from __future__ import annotations

import hashlib
import secrets
from pathlib import Path
from typing import Any

WIDTH = 1080
HEIGHT = 1350

THEMES: dict[str, dict[str, tuple[int, int, int]]] = {
    "lime": {
        "bg": (8, 10, 14),
        "bg2": (14, 22, 18),
        "panel": (18, 26, 22),
        "ink": (245, 248, 252),
        "muted": (160, 174, 192),
        "accent": (180, 255, 57),
        "accent2": (56, 210, 255),
        "line": (40, 55, 75),
        "card": (22, 28, 40),
    },
    "cyan": {
        "bg": (6, 12, 20),
        "bg2": (10, 28, 42),
        "panel": (14, 28, 40),
        "ink": (245, 250, 255),
        "muted": (150, 175, 195),
        "accent": (56, 210, 255),
        "accent2": (180, 255, 57),
        "line": (35, 60, 80),
        "card": (16, 30, 42),
    },
    "teal": {
        "bg": (6, 16, 18),
        "bg2": (10, 36, 38),
        "panel": (12, 32, 36),
        "ink": (240, 252, 250),
        "muted": (140, 180, 175),
        "accent": (45, 212, 191),
        "accent2": (125, 211, 252),
        "line": (30, 70, 70),
        "card": (14, 34, 38),
    },
    "amber": {
        "bg": (14, 10, 6),
        "bg2": (32, 22, 10),
        "panel": (36, 26, 14),
        "ink": (255, 250, 240),
        "muted": (190, 170, 140),
        "accent": (251, 191, 36),
        "accent2": (56, 210, 255),
        "line": (70, 55, 30),
        "card": (40, 28, 16),
    },
    "coral": {
        "bg": (14, 8, 10),
        "bg2": (36, 16, 20),
        "panel": (40, 18, 24),
        "ink": (255, 245, 245),
        "muted": (190, 160, 165),
        "accent": (251, 113, 133),
        "accent2": (56, 210, 255),
        "line": (80, 40, 50),
        "card": (42, 20, 26),
    },
    "steel": {
        "bg": (10, 12, 16),
        "bg2": (24, 28, 36),
        "panel": (28, 32, 42),
        "ink": (240, 244, 248),
        "muted": (150, 160, 175),
        "accent": (148, 163, 184),
        "accent2": (56, 210, 255),
        "line": (50, 58, 72),
        "card": (30, 34, 44),
    },
    "mint": {
        "bg": (6, 18, 14),
        "bg2": (12, 40, 30),
        "panel": (14, 36, 28),
        "ink": (240, 255, 248),
        "muted": (140, 185, 165),
        "accent": (52, 211, 153),
        "accent2": (180, 255, 57),
        "line": (30, 70, 55),
        "card": (16, 38, 30),
    },
    "sky": {
        "bg": (8, 14, 28),
        "bg2": (16, 36, 64),
        "panel": (18, 40, 68),
        "ink": (240, 248, 255),
        "muted": (150, 175, 210),
        "accent": (96, 165, 250),
        "accent2": (45, 212, 191),
        "line": (40, 70, 110),
        "card": (20, 42, 70),
    },
    "navy": {
        "bg": (6, 10, 24),
        "bg2": (12, 22, 48),
        "panel": (16, 28, 56),
        "ink": (245, 248, 255),
        "muted": (140, 160, 200),
        "accent": (99, 102, 241),
        "accent2": (56, 210, 255),
        "line": (40, 50, 90),
        "card": (18, 30, 58),
    },
    "emerald": {
        "bg": (6, 16, 12),
        "bg2": (10, 40, 28),
        "panel": (12, 38, 28),
        "ink": (240, 255, 248),
        "muted": (130, 180, 155),
        "accent": (16, 185, 129),
        "accent2": (251, 191, 36),
        "line": (25, 70, 50),
        "card": (14, 40, 30),
    },
}

THEME_KEYS = list(THEMES.keys())


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
        return {k: d for k in ("display", "hero", "h1", "h2", "h3", "body", "small", "tiny")}
    return {
        "display": ImageFont.truetype(bold, 58 * s),
        "hero": ImageFont.truetype(bold, 52 * s),
        "h1": ImageFont.truetype(bold, 42 * s),
        "h2": ImageFont.truetype(bold, 30 * s),
        "h3": ImageFont.truetype(bold, 24 * s),
        "body": ImageFont.truetype(reg, 22 * s),
        "small": ImageFont.truetype(reg, 18 * s),
        "tiny": ImageFont.truetype(reg, 15 * s),
    }


def _seed(post: dict[str, Any]) -> int:
    key = f"{post.get('topic')}|{post.get('image_title')}|{post.get('_variant')}"
    return int(hashlib.md5(key.encode()).hexdigest()[:8], 16)


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


def _palette(post: dict[str, Any]) -> dict[str, tuple[int, int, int]]:
    theme = (post.get("accent_theme") or "lime").lower()
    if theme not in THEMES:
        theme = THEME_KEYS[_seed(post) % len(THEME_KEYS)]
    return THEMES[theme]


def _gradient(img: Any, c1: tuple[int, int, int], c2: tuple[int, int, int]) -> None:
    from PIL import ImageDraw

    d = ImageDraw.Draw(img)
    for y in range(HEIGHT):
        t = y / max(HEIGHT - 1, 1)
        r = int(c1[0] + (c2[0] - c1[0]) * t)
        g = int(c1[1] + (c2[1] - c1[1]) * t)
        b = int(c1[2] + (c2[2] - c1[2]) * t)
        d.line([(0, y), (WIDTH, y)], fill=(r, g, b))


def _soft_blob(base: Any, xy: tuple[int, int], radius: int, color: tuple[int, int, int], alpha: int = 40) -> Any:
    from PIL import Image, ImageDraw, ImageFilter

    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    x, y = xy
    d.ellipse([x - radius, y - radius, x + radius, y + radius], fill=(*color, alpha))
    overlay = overlay.filter(ImageFilter.GaussianBlur(max(radius // 3, 8)))
    return Image.alpha_composite(base.convert("RGBA"), overlay)


def _grid(base: Any, color: tuple[int, int, int] = (56, 210, 255)) -> Any:
    from PIL import Image, ImageDraw

    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    step = max(36, WIDTH // 30)
    for x in range(0, WIDTH, step):
        d.line([(x, 0), (x, HEIGHT)], fill=(*color, 18), width=1)
    for y in range(0, HEIGHT, step):
        d.line([(0, y), (WIDTH, y)], fill=(*color, 18), width=1)
    return Image.alpha_composite(base.convert("RGBA"), overlay)


def _glow_rect(
    base: Any,
    box: tuple[int, int, int, int],
    color: tuple[int, int, int],
    panel: tuple[int, int, int],
    radius: int = 18,
) -> Any:
    from PIL import Image, ImageDraw, ImageFilter

    glow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.rounded_rectangle([box[0] - 4, box[1] - 4, box[2] + 4, box[3] + 4], radius=radius + 4, fill=(*color, 55))
    glow = glow.filter(ImageFilter.GaussianBlur(10))
    panel_img = Image.new("RGBA", base.size, (0, 0, 0, 0))
    pd = ImageDraw.Draw(panel_img)
    pd.rounded_rectangle(list(box), radius=radius, fill=(*panel, 230), outline=(*color, 220), width=2)
    return Image.alpha_composite(Image.alpha_composite(base.convert("RGBA"), glow), panel_img)


def _icon_box(draw: Any, xy: tuple[int, int], kind: str, size: int, color: tuple[int, int, int]) -> None:
    x, y = xy
    draw.rounded_rectangle([x, y, x + size, y + size], radius=6, outline=color, width=2)
    cx, cy = x + size // 2, y + size // 2
    c = color
    if kind == "data":
        draw.rectangle([cx - 8, cy - 8, cx + 8, cy + 8], outline=c, width=2)
        draw.line([(cx - 8, cy), (cx + 8, cy)], fill=c, width=2)
    elif kind == "flow":
        draw.polygon(
            [
                (cx - 10, cy),
                (cx + 2, cy - 9),
                (cx + 2, cy - 3),
                (cx + 10, cy - 3),
                (cx + 10, cy + 3),
                (cx + 2, cy + 3),
                (cx + 2, cy + 9),
            ],
            fill=c,
        )
    elif kind == "link":
        draw.arc([cx - 10, cy - 7, cx - 1, cy + 7], 0, 360, fill=c, width=2)
        draw.arc([cx + 1, cy - 7, cx + 10, cy + 7], 0, 360, fill=c, width=2)
    elif kind == "test":
        draw.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], outline=c, width=2)
        draw.line([(cx - 4, cy), (cx - 1, cy + 4), (cx + 6, cy - 5)], fill=c, width=2)
    elif kind == "clock":
        draw.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], outline=c, width=2)
        draw.line([(cx, cy), (cx, cy - 6)], fill=c, width=2)
        draw.line([(cx, cy), (cx + 5, cy + 2)], fill=c, width=2)
    elif kind == "shield":
        draw.polygon(
            [(cx, cy - 10), (cx + 10, cy - 4), (cx + 8, cy + 8), (cx, cy + 12), (cx - 8, cy + 8), (cx - 10, cy - 4)],
            outline=c,
        )
    elif kind == "doc":
        draw.rectangle([cx - 7, cy - 9, cx + 7, cy + 9], outline=c, width=2)
        draw.line([(cx - 3, cy - 3), (cx + 3, cy - 3)], fill=c, width=2)
    else:
        draw.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=c)


def _base_canvas(post: dict[str, Any], pal: dict[str, tuple[int, int, int]]) -> Any:
    from PIL import Image

    img = Image.new("RGB", (WIDTH, HEIGHT))
    _gradient(img, pal["bg"], pal["bg2"])
    img = _grid(img, pal["accent2"])
    seed = _seed(post)
    img = _soft_blob(img, (200 + (seed % 500), 300 + (seed % 400)), 220 + (seed % 80), pal["accent"], 26)
    img = _soft_blob(img, (700 + (seed % 300), 900 + (seed % 200)), 200 + (seed % 60), pal["accent2"], 20)
    return img


def _chip(d: Any, fonts: dict[str, Any], xy: tuple[int, int], text: str, pal: dict[str, tuple[int, int, int]]) -> None:
    d.rounded_rectangle([xy[0], xy[1], xy[0] + 180, xy[1] + 40], radius=10, fill=pal["panel"], outline=pal["line"], width=1)
    d.text((xy[0] + 14, xy[1] + 10), text[:22], font=fonts["tiny"], fill=pal["accent2"])


def _footer(d: Any, fonts: dict[str, Any], post: dict[str, Any], pal: dict[str, tuple[int, int, int]]) -> None:
    foot = (post.get("footer_note") or "FHIR · CMS · Interoperability · HealthIT")[:90]
    tw = d.textlength(foot, font=fonts["tiny"])
    d.text(((WIDTH - tw) / 2, HEIGHT - 48), foot, font=fonts["tiny"], fill=pal["muted"])


def _layout_hud_alert(post: dict[str, Any], fonts: dict[str, Any]) -> Any:
    from PIL import ImageDraw

    pal = _palette(post)
    img = _base_canvas(post, pal)
    d = ImageDraw.Draw(img)
    _chip(d, fonts, (36, 28), "INTEROP BRIEF", pal)

    alert = (post.get("alert_label") or "DON'T DELAY").upper()
    aw = int(d.textlength(alert, font=fonts["small"]) + 48)
    img = _glow_rect(img, (36, 90, 36 + aw, 138), pal["accent"], pal["panel"], 16)
    d = ImageDraw.Draw(img)
    d.text((60, 102), f"!  {alert}", font=fonts["small"], fill=pal["accent"])

    title = (post.get("image_title") or post.get("hook") or "CMS Interoperability").strip()
    y = 170
    for line in _wrap(title, fonts["h1"], WIDTH - 100, d)[:3]:
        d.text((36, y), line, font=fonts["h1"], fill=pal["ink"])
        y += 54

    highlight = (post.get("highlight") or post.get("image_subtitle") or "").strip()
    if highlight:
        for line in _wrap(highlight, fonts["display"], WIDTH - 100, d)[:2]:
            d.text((36, y), line, font=fonts["display"], fill=pal["accent"])
            y += 64

    intro = (post.get("intro") or "").strip()
    if intro:
        for line in _wrap(intro, fonts["body"], WIDTH - 100, d)[:3]:
            d.text((36, y), line, font=fonts["body"], fill=pal["muted"])
            y += 30

    badges = list(post.get("badge_labels") or ["FHIR", "CMS", "API"])[:4]
    y += 16
    bx = 36
    for badge in badges:
        label = str(badge)[:16]
        tw = int(d.textlength(label, font=fonts["small"]))
        img = _glow_rect(img, (bx, y, bx + tw + 36, y + 44), pal["accent2"], pal["panel"], 14)
        d = ImageDraw.Draw(img)
        d.text((bx + 18, y + 10), label, font=fonts["small"], fill=pal["accent2"])
        bx += tw + 52
    y += 70

    bullets = list(post.get("bullets") or ["Build", "Test", "Validate", "Ship"])[:4]
    kinds = ["data", "flow", "link", "test"]
    for i, b in enumerate(bullets):
        box = (36, y, WIDTH - 36, y + 100)
        img = _glow_rect(img, box, pal["accent"] if i % 2 == 0 else pal["accent2"], pal["panel"], 16)
        d = ImageDraw.Draw(img)
        _icon_box(d, (56, y + 32), kinds[i % 4], 36, pal["accent"])
        ty = y + 28
        for line in _wrap(str(b), fonts["h3"], WIDTH - 160, d)[:2]:
            d.text((110, ty), line, font=fonts["h3"], fill=pal["ink"])
            ty += 34
        y += 114

    cta = (post.get("cta") or "Is your organization ready?").strip()
    img = _glow_rect(img, (36, HEIGHT - 140, WIDTH - 36, HEIGHT - 70), pal["accent"], pal["panel"], 18)
    d = ImageDraw.Draw(img)
    d.text((60, HEIGHT - 118), cta[:68], font=fonts["h3"], fill=pal["ink"])
    _footer(d, fonts, post, pal)
    return img


def _layout_hud_workflow(post: dict[str, Any], fonts: dict[str, Any]) -> Any:
    from PIL import ImageDraw

    pal = _palette(post)
    img = _base_canvas(post, pal)
    d = ImageDraw.Draw(img)
    _chip(d, fonts, (36, 28), "PRIOR AUTH FLOW", pal)

    title = (post.get("image_title") or "CRD → DTR → PAS").strip()
    y = 100
    for line in _wrap(title, fonts["hero"], WIDTH - 80, d)[:2]:
        d.text((36, y), line, font=fonts["hero"], fill=pal["ink"])
        y += 58
    sub = (post.get("highlight") or post.get("image_subtitle") or "Real-time prior authorization").strip()
    for line in _wrap(sub, fonts["body"], WIDTH - 80, d)[:2]:
        d.text((36, y), line, font=fonts["body"], fill=pal["muted"])
        y += 30

    steps = list(
        post.get("steps")
        or post.get("bullets")
        or ["CRD identifies requirements", "DTR gathers documentation", "PAS submits authorization"]
    )[:4]
    y += 40
    for i, step in enumerate(steps):
        box = (36, y, WIDTH - 36, y + 160)
        img = _glow_rect(img, box, pal["accent"], pal["panel"], 20)
        d = ImageDraw.Draw(img)
        d.ellipse([60, y + 50, 120, y + 110], outline=pal["accent"], width=3)
        num = f"{i + 1}"
        nw = d.textlength(num, font=fonts["h2"])
        d.text((90 - nw / 2, y + 62), num, font=fonts["h2"], fill=pal["accent"])
        ty = y + 48
        for line in _wrap(str(step), fonts["h2"], WIDTH - 220, d)[:2]:
            d.text((150, ty), line, font=fonts["h2"], fill=pal["ink"])
            ty += 40
        if i < len(steps) - 1:
            d.line([(90, y + 160), (90, y + 190)], fill=pal["accent2"], width=3)
        y += 190

    cta = (post.get("cta") or "FHIR moves healthcare toward real-time decisions.").strip()
    img = _glow_rect(img, (36, HEIGHT - 120, WIDTH - 36, HEIGHT - 50), pal["accent2"], pal["panel"], 16)
    d = ImageDraw.Draw(img)
    d.text((56, HEIGHT - 98), cta[:64], font=fonts["h3"], fill=pal["ink"])
    _footer(d, fonts, post, pal)
    return img


def _layout_hud_pillars(post: dict[str, Any], fonts: dict[str, Any]) -> Any:
    from PIL import ImageDraw

    pal = _palette(post)
    img = _base_canvas(post, pal)
    d = ImageDraw.Draw(img)
    _chip(d, fonts, (36, 28), "CMS-0057-F", pal)

    title = (post.get("image_title") or "Four APIs reshaping interoperability").strip()
    y = 100
    for line in _wrap(title, fonts["h1"], WIDTH - 80, d)[:3]:
        d.text((36, y), line, font=fonts["h1"], fill=pal["ink"])
        y += 52
    highlight = (post.get("highlight") or "Ready for 2027?").strip()
    d.text((36, y + 8), highlight[:40], font=fonts["display"], fill=pal["accent"])

    pillars = list(
        post.get("bullets") or ["Patient Access", "Provider Access", "Payer-to-Payer", "Prior Authorization"]
    )[:4]
    start_y = 360
    for i, p in enumerate(pillars):
        col = i % 2
        row = i // 2
        x0 = 36 + col * 520
        y0 = start_y + row * 280
        box = (x0, y0, x0 + 488, y0 + 240)
        img = _glow_rect(img, box, pal["accent"] if i % 2 == 0 else pal["accent2"], pal["panel"], 20)
        d = ImageDraw.Draw(img)
        d.text((x0 + 36, y0 + 40), f"0{i + 1}", font=fonts["h2"], fill=pal["accent"])
        for j, line in enumerate(_wrap(str(p), fonts["h2"], 400, d)[:3]):
            d.text((x0 + 36, y0 + 100 + j * 40), line, font=fonts["h2"], fill=pal["ink"])

    cta = (post.get("cta") or "Is your organization ready for 2027?").strip()
    img = _glow_rect(img, (36, HEIGHT - 120, WIDTH - 36, HEIGHT - 50), pal["accent"], pal["panel"], 16)
    d = ImageDraw.Draw(img)
    d.text((56, HEIGHT - 98), cta[:64], font=fonts["h3"], fill=pal["ink"])
    _footer(d, fonts, post, pal)
    return img


def _layout_hud_quote(post: dict[str, Any], fonts: dict[str, Any]) -> Any:
    from PIL import ImageDraw

    pal = _palette(post)
    img = _base_canvas(post, pal)
    d = ImageDraw.Draw(img)
    _chip(d, fonts, (36, 40), "HEALTH IT", pal)

    quote = (post.get("image_title") or post.get("hook") or "Where do you see the biggest opportunity?").strip()
    y = 280
    d.text((36, y), '"', font=fonts["display"], fill=pal["accent"])
    y = 360
    for line in _wrap(quote, fonts["hero"], WIDTH - 100, d)[:5]:
        d.text((60, y), line, font=fonts["hero"], fill=pal["ink"])
        y += 64

    sub = (post.get("highlight") or post.get("image_subtitle") or "").strip()
    if sub:
        y += 30
        for line in _wrap(sub, fonts["body"], WIDTH - 120, d)[:3]:
            d.text((60, y), line, font=fonts["body"], fill=pal["muted"])
            y += 32

    badges = list(post.get("badge_labels") or ["FHIR", "Cloud", "AI", "APIs"])[:4]
    y = max(y + 60, HEIGHT - 280)
    bx = 60
    for badge in badges:
        tw = int(d.textlength(str(badge)[:14], font=fonts["small"]))
        img = _glow_rect(img, (bx, y, bx + tw + 40, y + 48), pal["accent2"], pal["panel"], 14)
        d = ImageDraw.Draw(img)
        d.text((bx + 20, y + 12), str(badge)[:14], font=fonts["small"], fill=pal["accent2"])
        bx += tw + 56

    cta = (post.get("cta") or "Connected. Automated. Interoperable.").strip()
    img = _glow_rect(img, (36, HEIGHT - 120, WIDTH - 36, HEIGHT - 50), pal["accent"], pal["panel"], 16)
    d = ImageDraw.Draw(img)
    d.text((56, HEIGHT - 98), cta[:64], font=fonts["h3"], fill=pal["ink"])
    _footer(d, fonts, post, pal)
    return img


def _layout_hud_split(post: dict[str, Any], fonts: dict[str, Any]) -> Any:
    from PIL import ImageDraw

    pal = _palette(post)
    img = _base_canvas(post, pal)
    d = ImageDraw.Draw(img)
    _chip(d, fonts, (36, 28), "COMPARE", pal)

    title = (post.get("image_title") or "Two realities").strip()
    y = 100
    for line in _wrap(title, fonts["h1"], WIDTH - 80, d)[:2]:
        d.text((36, y), line, font=fonts["h1"], fill=pal["ink"])
        y += 54

    mid = WIDTH // 2
    left = (36, 240, mid - 18, HEIGHT - 160)
    right = (mid + 18, 240, WIDTH - 36, HEIGHT - 160)
    img = _glow_rect(img, left, pal["muted"], pal["panel"], 22)
    img = _glow_rect(img, right, pal["accent"], pal["panel"], 22)
    d = ImageDraw.Draw(img)

    left_label = post.get("left_label") or "Before"
    right_label = post.get("right_label") or "With FHIR"
    left_points = list(post.get("left_points") or ["Manual", "Slow", "Fragile"])[:3]
    right_points = list(post.get("right_points") or ["API-first", "Faster", "Scalable"])[:3]

    for box, label, points, color in (
        (left, left_label, left_points, pal["muted"]),
        (right, right_label, right_points, pal["accent"]),
    ):
        cx = (box[0] + box[2]) // 2
        tw = d.textlength(str(label)[:24], font=fonts["h2"])
        d.text((cx - tw / 2, box[1] + 36), str(label)[:24], font=fonts["h2"], fill=color)
        yy = box[1] + 120
        for p in points:
            d.rounded_rectangle(
                [box[0] + 24, yy, box[2] - 24, yy + 90], radius=14, fill=pal["card"], outline=color, width=1
            )
            for j, line in enumerate(_wrap(str(p), fonts["body"], box[2] - box[0] - 80, d)[:2]):
                d.text((box[0] + 44, yy + 24 + j * 28), line, font=fonts["body"], fill=pal["ink"])
            yy += 110

    cta = (post.get("cta") or "Choose the architecture that scales.").strip()
    img = _glow_rect(img, (36, HEIGHT - 120, WIDTH - 36, HEIGHT - 50), pal["accent"], pal["panel"], 16)
    d = ImageDraw.Draw(img)
    d.text((56, HEIGHT - 98), cta[:64], font=fonts["h3"], fill=pal["ink"])
    _footer(d, fonts, post, pal)
    return img


def _layout_hud_points(post: dict[str, Any], fonts: dict[str, Any]) -> Any:
    from PIL import ImageDraw

    pal = _palette(post)
    img = _base_canvas(post, pal)
    d = ImageDraw.Draw(img)
    _chip(d, fonts, (36, 28), "KEY INSIGHTS", pal)

    title = (post.get("image_title") or post.get("hook") or "FHIR Interoperability").strip()
    y = 100
    for line in _wrap(title, fonts["hero"], WIDTH - 80, d)[:3]:
        d.text((36, y), line, font=fonts["hero"], fill=pal["ink"])
        y += 58
    sub = (post.get("highlight") or post.get("image_subtitle") or "").strip()
    if sub:
        for line in _wrap(sub, fonts["h2"], WIDTH - 80, d)[:2]:
            d.text((36, y), line, font=fonts["h2"], fill=pal["accent"])
            y += 40

    bullets = list(post.get("bullets") or ["Point one", "Point two", "Point three", "Point four"])[:4]
    kinds = ["data", "flow", "link", "test"]
    y += 24
    for i, b in enumerate(bullets):
        box = (36, y, WIDTH - 36, y + 140)
        img = _glow_rect(img, box, pal["accent"] if i % 2 == 0 else pal["accent2"], pal["panel"], 18)
        d = ImageDraw.Draw(img)
        _icon_box(d, (60, y + 50), kinds[i % 4], 40, pal["accent"])
        d.text((120, y + 28), f"{i + 1:02d}", font=fonts["h2"], fill=pal["accent"])
        ty = y + 70
        for line in _wrap(str(b), fonts["h3"], WIDTH - 200, d)[:2]:
            d.text((120, ty), line, font=fonts["h3"], fill=pal["ink"])
            ty += 34
        y += 156

    cta = (post.get("cta") or "Standards create the contract.").strip()
    img = _glow_rect(img, (36, HEIGHT - 120, WIDTH - 36, HEIGHT - 50), pal["accent"], pal["panel"], 16)
    d = ImageDraw.Draw(img)
    d.text((56, HEIGHT - 98), cta[:70], font=fonts["h3"], fill=pal["ink"])
    _footer(d, fonts, post, pal)
    return img


def _layout_hud_grid(post: dict[str, Any], fonts: dict[str, Any]) -> Any:
    from PIL import ImageDraw

    pal = _palette(post)
    img = _base_canvas(post, pal)
    d = ImageDraw.Draw(img)
    _chip(d, fonts, (36, 28), "PROVIDER DATA", pal)

    title = (post.get("image_title") or "Accurate provider data").strip()
    y = 100
    for line in _wrap(title, fonts["h1"], WIDTH - 80, d)[:2]:
        d.text((36, y), line, font=fonts["h1"], fill=pal["ink"])
        y += 52
    sub = (post.get("highlight") or "").strip()
    if sub:
        d.text((36, y), sub[:50], font=fonts["h3"], fill=pal["muted"])

    cards = list(post.get("bullets") or ["Standardized", "Searchable", "Fresh", "Trusted"])[:4]
    start_y = 280
    for i, card in enumerate(cards):
        col, row = i % 2, i // 2
        x0 = 36 + col * 520
        y0 = start_y + row * 340
        box = (x0, y0, x0 + 488, y0 + 300)
        img = _glow_rect(img, box, pal["accent"] if i % 2 else pal["accent2"], pal["panel"], 22)
        d = ImageDraw.Draw(img)
        _icon_box(d, (x0 + 40, y0 + 50), ["data", "link", "test", "flow"][i], 48, pal["accent"])
        for j, line in enumerate(_wrap(str(card), fonts["h2"], 400, d)[:4]):
            d.text((x0 + 40, y0 + 140 + j * 38), line, font=fonts["h2"], fill=pal["ink"])

    cta = (post.get("cta") or "Care coordination starts with clean directory data.").strip()
    img = _glow_rect(img, (36, HEIGHT - 120, WIDTH - 36, HEIGHT - 50), pal["accent"], pal["panel"], 16)
    d = ImageDraw.Draw(img)
    d.text((56, HEIGHT - 98), cta[:64], font=fonts["h3"], fill=pal["ink"])
    _footer(d, fonts, post, pal)
    return img


def _layout_hud_stack(post: dict[str, Any], fonts: dict[str, Any]) -> Any:
    from PIL import ImageDraw

    pal = _palette(post)
    img = _base_canvas(post, pal)
    d = ImageDraw.Draw(img)
    _chip(d, fonts, (36, 28), "DATA EXCHANGE", pal)

    title = (post.get("image_title") or "Continuity when members change plans").strip()
    y = 100
    for line in _wrap(title, fonts["h1"], WIDTH - 80, d)[:3]:
        d.text((36, y), line, font=fonts["h1"], fill=pal["ink"])
        y += 52

    steps = list(
        post.get("steps")
        or post.get("bullets")
        or ["Member switches plan", "Payer-to-Payer exchange", "Clinical continuity", "Better experience"]
    )[:4]
    y += 40
    for i, step in enumerate(steps):
        box = (80, y, WIDTH - 80, y + 130)
        img = _glow_rect(img, box, pal["accent"] if i % 2 == 0 else pal["accent2"], pal["panel"], 18)
        d = ImageDraw.Draw(img)
        d.ellipse([100, y + 40, 160, y + 100], fill=pal["card"], outline=pal["accent"], width=2)
        d.text((118, y + 52), f"{i + 1}", font=fonts["h2"], fill=pal["accent"])
        for j, line in enumerate(_wrap(str(step), fonts["h3"], WIDTH - 280, d)[:2]):
            d.text((190, y + 42 + j * 34), line, font=fonts["h3"], fill=pal["ink"])
        if i < len(steps) - 1:
            d.polygon(
                [(WIDTH // 2 - 14, y + 138), (WIDTH // 2 + 14, y + 138), (WIDTH // 2, y + 158)],
                fill=pal["accent2"],
            )
        y += 175

    cta = (post.get("cta") or "Healthcare data shouldn't stop moving.").strip()
    img = _glow_rect(img, (36, HEIGHT - 120, WIDTH - 36, HEIGHT - 50), pal["accent"], pal["panel"], 16)
    d = ImageDraw.Draw(img)
    d.text((56, HEIGHT - 98), cta[:64], font=fonts["h3"], fill=pal["ink"])
    _footer(d, fonts, post, pal)
    return img


def _layout_hud_security(post: dict[str, Any], fonts: dict[str, Any]) -> Any:
    from PIL import ImageDraw

    pal = _palette(post)
    img = _base_canvas(post, pal)
    d = ImageDraw.Draw(img)
    _chip(d, fonts, (36, 28), "API SECURITY", pal)

    title = (post.get("image_title") or "Interoperability starts with trust").strip()
    y = 100
    for line in _wrap(title, fonts["hero"], WIDTH - 80, d)[:3]:
        d.text((36, y), line, font=fonts["hero"], fill=pal["ink"])
        y += 58
    sub = (post.get("highlight") or "Protect data. Enable innovation.").strip()
    d.text((36, y), sub[:55], font=fonts["h3"], fill=pal["muted"])

    items = list(post.get("bullets") or ["OAuth 2.0", "SMART on FHIR", "Secure API design", "Least-privilege scopes"])[:4]
    y = 320
    for i, item in enumerate(items):
        box = (36, y, WIDTH - 36, y + 150)
        img = _glow_rect(img, box, pal["accent"], pal["panel"], 18)
        d = ImageDraw.Draw(img)
        _icon_box(d, (60, y + 50), "shield" if i % 2 == 0 else "link", 48, pal["accent"])
        for j, line in enumerate(_wrap(str(item), fonts["h2"], WIDTH - 200, d)[:2]):
            d.text((140, y + 50 + j * 40), line, font=fonts["h2"], fill=pal["ink"])
        y += 170

    cta = (post.get("cta") or "Trust is the first interoperability requirement.").strip()
    img = _glow_rect(img, (36, HEIGHT - 120, WIDTH - 36, HEIGHT - 50), pal["accent2"], pal["panel"], 16)
    d = ImageDraw.Draw(img)
    d.text((56, HEIGHT - 98), cta[:64], font=fonts["h3"], fill=pal["ink"])
    _footer(d, fonts, post, pal)
    return img


def _layout_hud_hero(post: dict[str, Any], fonts: dict[str, Any]) -> Any:
    from PIL import ImageDraw

    pal = _palette(post)
    img = _base_canvas(post, pal)
    d = ImageDraw.Draw(img)
    _chip(d, fonts, (36, 40), ".NET + HEALTHCARE", pal)

    title = (post.get("image_title") or ".NET 10 for modern FHIR APIs").strip()
    y = 200
    for line in _wrap(title, fonts["display"], WIDTH - 100, d)[:4]:
        d.text((36, y), line, font=fonts["display"], fill=pal["ink"])
        y += 70

    highlight = (post.get("highlight") or "Performance · Security · Scale").strip()
    y += 20
    for line in _wrap(highlight, fonts["h2"], WIDTH - 100, d)[:2]:
        d.text((36, y), line, font=fonts["h2"], fill=pal["accent"])
        y += 44

    bullets = list(post.get("bullets") or ["Performance", "Security", "Scalability"])[:3]
    y += 50
    for i, b in enumerate(bullets):
        box = (36, y, WIDTH - 36, y + 110)
        img = _glow_rect(img, box, pal["accent"] if i % 2 == 0 else pal["accent2"], pal["panel"], 16)
        d = ImageDraw.Draw(img)
        d.text((60, y + 36), f"{i + 1:02d}  {str(b)[:48]}", font=fonts["h2"], fill=pal["ink"])
        y += 130

    cta = (post.get("cta") or "What feature are you most excited about?").strip()
    img = _glow_rect(img, (36, HEIGHT - 120, WIDTH - 36, HEIGHT - 50), pal["accent"], pal["panel"], 16)
    d = ImageDraw.Draw(img)
    d.text((56, HEIGHT - 98), cta[:64], font=fonts["h3"], fill=pal["ink"])
    _footer(d, fonts, post, pal)
    return img


LAYOUTS = {
    "hud_alert": _layout_hud_alert,
    "hud_workflow": _layout_hud_workflow,
    "hud_pillars": _layout_hud_pillars,
    "hud_quote": _layout_hud_quote,
    "hud_split": _layout_hud_split,
    "hud_points": _layout_hud_points,
    "hud_grid": _layout_hud_grid,
    "hud_stack": _layout_hud_stack,
    "hud_security": _layout_hud_security,
    "hud_hero": _layout_hud_hero,
    "dark_tech": _layout_hud_alert,
    "split_compare": _layout_hud_split,
    "key_points": _layout_hud_points,
    "before_after": _layout_hud_stack,
    "workflow": _layout_hud_workflow,
    "title_network": _layout_hud_quote,
}

UNIQUE_LAYOUT_KEYS = [
    "hud_alert",
    "hud_workflow",
    "hud_pillars",
    "hud_quote",
    "hud_split",
    "hud_points",
    "hud_grid",
    "hud_stack",
    "hud_security",
    "hud_hero",
]


def _enrich(post: dict[str, Any]) -> dict[str, Any]:
    p = dict(post)
    p["_variant"] = secrets.token_hex(4)

    layout = (p.get("image_layout") or "").lower()
    if layout not in LAYOUTS:
        layout = UNIQUE_LAYOUT_KEYS[_seed(p) % len(UNIQUE_LAYOUT_KEYS)]
    p["image_layout"] = layout

    theme = (p.get("accent_theme") or "").lower()
    if theme not in THEMES:
        p["accent_theme"] = THEME_KEYS[(_seed(p) + 3) % len(THEME_KEYS)]
    elif secrets.randbelow(3) == 0:
        p["accent_theme"] = THEME_KEYS[(_seed(p) + secrets.randbelow(len(THEME_KEYS))) % len(THEME_KEYS)]

    p.setdefault("alert_label", "HEALTH IT")
    p.setdefault("cta", "Is your organization ready?")
    return p


def create_post_image(post: dict[str, Any], out_path: Path) -> Path:
    global WIDTH, HEIGHT

    post = _enrich(post)
    layout = post["image_layout"]
    WIDTH, HEIGHT = 1080, 1350
    fonts = _fonts(scale=1)

    img = LAYOUTS[layout](post, fonts)
    if img.mode != "RGB":
        img = img.convert("RGB")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, format="PNG", compress_level=4)
    print(f"[image] '{layout}' / theme={post.get('accent_theme')} -> {out_path.name}")
    return out_path
