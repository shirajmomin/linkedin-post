"""Premium LinkedIn HUD / HealthTech visuals (1080x1350).

Dark neon canvas with grid + glow — no photo/skeleton backgrounds.
No author name on the image.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

WIDTH = 1080
HEIGHT = 1350

# Neon HealthTech palette (sample-inspired)
HUD = {
    "bg": (8, 10, 14),
    "bg2": (16, 22, 32),
    "panel": (18, 24, 34),
    "panel2": (24, 32, 46),
    "ink": (245, 248, 252),
    "muted": (160, 174, 192),
    "lime": (180, 255, 57),
    "lime_dim": (120, 190, 40),
    "cyan": (56, 210, 255),
    "cyan_dim": (30, 140, 180),
    "red": (255, 70, 70),
    "line": (40, 55, 75),
    "card": (22, 28, 40),
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
    key = f"{post.get('topic')}|{post.get('image_title')}|{post.get('hook')}"
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


def _grid(base: Any) -> Any:
    from PIL import Image, ImageDraw

    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    step = max(36, WIDTH // 30)
    for x in range(0, WIDTH, step):
        d.line([(x, 0), (x, HEIGHT)], fill=(56, 210, 255, 18), width=1)
    for y in range(0, HEIGHT, step):
        d.line([(0, y), (WIDTH, y)], fill=(56, 210, 255, 18), width=1)
    # vignette corners via ellipses
    d.ellipse([-200, -200, 420, 420], outline=(180, 255, 57, 28), width=2)
    d.ellipse([WIDTH - 420, HEIGHT - 420, WIDTH + 200, HEIGHT + 200], outline=(56, 210, 255, 28), width=2)
    return Image.alpha_composite(base.convert("RGBA"), overlay)


def _glow_rect(base: Any, box: tuple[int, int, int, int], color: tuple[int, int, int], radius: int = 18) -> Any:
    from PIL import Image, ImageDraw, ImageFilter

    glow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.rounded_rectangle([box[0] - 4, box[1] - 4, box[2] + 4, box[3] + 4], radius=radius + 4, fill=(*color, 60))
    glow = glow.filter(ImageFilter.GaussianBlur(10))
    panel = Image.new("RGBA", base.size, (0, 0, 0, 0))
    pd = ImageDraw.Draw(panel)
    pd.rounded_rectangle(list(box), radius=radius, fill=(*HUD["panel"], 230), outline=(*color, 220), width=2)
    return Image.alpha_composite(Image.alpha_composite(base.convert("RGBA"), glow), panel)


def _icon_box(draw: Any, xy: tuple[int, int], kind: str, size: int = 34) -> None:
    x, y = xy
    draw.rounded_rectangle([x, y, x + size, y + size], radius=6, outline=HUD["lime"], width=2)
    cx, cy = x + size // 2, y + size // 2
    c = HUD["lime"]
    if kind == "data":
        draw.rectangle([cx - 8, cy - 8, cx + 8, cy + 8], outline=c, width=2)
        draw.line([(cx - 8, cy), (cx + 8, cy)], fill=c, width=2)
    elif kind == "flow":
        draw.polygon([(cx - 10, cy), (cx + 2, cy - 9), (cx + 2, cy - 3), (cx + 10, cy - 3), (cx + 10, cy + 3), (cx + 2, cy + 3), (cx + 2, cy + 9)], fill=c)
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
    elif kind == "patient":
        draw.ellipse([cx - 5, cy - 10, cx + 5, cy - 1], fill=c)
        draw.ellipse([cx - 10, cy + 1, cx + 10, cy + 12], fill=c)
    elif kind == "doc":
        draw.rectangle([cx - 7, cy - 9, cx + 7, cy + 9], outline=c, width=2)
        draw.line([(cx - 3, cy - 3), (cx + 3, cy - 3)], fill=c, width=2)
    else:
        draw.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=c)


def _layout_hud_alert(post: dict[str, Any], fonts: dict[str, Any]) -> Any:
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (WIDTH, HEIGHT))
    _gradient(img, HUD["bg"], HUD["bg2"])
    img = _grid(img)
    # Soft glow blobs only — no skeleton / photo background
    img = _soft_blob(img, (900, 420), 280, HUD["cyan"], 28)
    img = _soft_blob(img, (200, 1100), 220, HUD["lime"], 18)

    left_w = WIDTH - 72
    d = ImageDraw.Draw(img)

    # Brand chip (generic — no personal name)
    d.rounded_rectangle([36, 28, 210, 68], radius=10, fill=HUD["panel"], outline=HUD["line"], width=1)
    d.text((50, 38), "INTEROP BRIEF", font=fonts["tiny"], fill=HUD["cyan"])

    # Alert pill
    alert = (post.get("alert_label") or "DON'T DELAY").upper()
    aw = d.textlength(alert, font=fonts["small"]) + 48
    img = _glow_rect(img, (36, 90, 36 + int(aw), 138), HUD["lime"], radius=16)
    d = ImageDraw.Draw(img)
    d.text((60, 102), f"!  {alert}", font=fonts["small"], fill=HUD["lime"])

    # Title
    title = (post.get("image_title") or post.get("hook") or "CMS Interoperability").strip()
    y = 170
    for line in _wrap(title, fonts["h1"], left_w - 40, d)[:3]:
        d.text((36, y), line, font=fonts["h1"], fill=HUD["ink"])
        y += 54

    # Highlight (deadline / punch line)
    highlight = (post.get("highlight") or post.get("image_subtitle") or "").strip()
    if highlight:
        y += 6
        for line in _wrap(highlight, fonts["display"], left_w - 40, d)[:2]:
            d.text((36, y), line, font=fonts["display"], fill=HUD["lime"])
            y += 64
        support = (post.get("support_line") or "").strip()
        if support:
            for line in _wrap(support, fonts["body"], left_w - 40, d)[:2]:
                d.text((36, y), line, font=fonts["body"], fill=HUD["cyan"])
                y += 30

    # Intro
    intro = (post.get("intro") or "").strip()
    if not intro and not highlight:
        intro = "Standards create the contract. Delivery creates the outcome."
    if intro:
        y += 8
        for line in _wrap(intro, fonts["body"], left_w - 40, d)[:3]:
            d.text((36, y), line, font=fonts["body"], fill=HUD["muted"])
            y += 30

    # Topic chips row
    badges = list(post.get("badge_labels") or post.get("rail_labels") or ["FHIR", "CMS", "API"])[:4]
    y += 20
    bx = 36
    for badge in badges:
        label = str(badge)[:16]
        tw = d.textlength(label, font=fonts["small"])
        img = _glow_rect(img, (bx, y, bx + int(tw) + 36, y + 44), HUD["cyan"], radius=14)
        d = ImageDraw.Draw(img)
        d.text((bx + 18, y + 10), label, font=fonts["small"], fill=HUD["cyan"])
        bx += int(tw) + 52
    y += 70

    # Bullets with neon icon boxes — full width
    bullets = list(post.get("bullets") or [])[:4]
    if not bullets:
        bullets = [
            "Prior Auth APIs must be production-ready",
            "CRD / DTR / PAS need end-to-end testing",
            "Directory + clinical context must connect",
            "Late testing creates go-live risk",
        ]
    kinds = ["data", "flow", "link", "test"]
    for i, b in enumerate(bullets):
        box = (36, y, WIDTH - 36, y + 110)
        img = _glow_rect(img, box, HUD["lime"] if i % 2 == 0 else HUD["cyan"], radius=16)
        d = ImageDraw.Draw(img)
        _icon_box(d, (56, y + 36), kinds[i % 4], 36)
        ty = y + 28
        for line in _wrap(str(b), fonts["h3"], WIDTH - 160, d)[:2]:
            d.text((110, ty), line, font=fonts["h3"], fill=HUD["ink"])
            ty += 34
        y += 126

    # CTA bar
    cta = (post.get("cta") or "The deadline is closer than it looks. Start now.").strip()
    cta_box = (36, HEIGHT - 150, WIDTH - 36, HEIGHT - 78)
    img = _glow_rect(img, cta_box, HUD["lime"], radius=18)
    d = ImageDraw.Draw(img)
    _icon_box(d, (58, HEIGHT - 132), "clock", 34)
    d.text((110, HEIGHT - 128), cta[:70], font=fonts["h3"], fill=HUD["ink"])

    # Footer note
    foot = (post.get("footer_note") or "FHIR · CMS · Interoperability · HealthIT")[:90]
    tw = d.textlength(foot, font=fonts["tiny"])
    d.text(((WIDTH - tw) / 2, HEIGHT - 55), foot, font=fonts["tiny"], fill=HUD["muted"])
    return img


def _layout_hud_split(post: dict[str, Any], fonts: dict[str, Any]) -> Any:
    """Dark neon split compare (HL7 vs FHIR style, HUD edition)."""
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (WIDTH, HEIGHT))
    _gradient(img, HUD["bg"], HUD["bg2"])
    img = _grid(img)
    d = ImageDraw.Draw(img)

    title = (post.get("image_title") or "Two standards. Two realities.").strip()
    d.text((40, 50), "INTEROP BRIEF", font=fonts["tiny"], fill=HUD["cyan"])
    y = 100
    for line in _wrap(title, fonts["h1"], WIDTH - 80, d)[:2]:
        d.text((40, y), line, font=fonts["h1"], fill=HUD["ink"])
        y += 54

    mid = WIDTH // 2
    left = (36, 240, mid - 18, HEIGHT - 160)
    right = (mid + 18, 240, WIDTH - 36, HEIGHT - 160)
    img = _glow_rect(img, left, HUD["muted"], 22)
    img = _glow_rect(img, right, HUD["lime"], 22)
    d = ImageDraw.Draw(img)

    left_label = post.get("left_label") or "Legacy"
    right_label = post.get("right_label") or "FHIR"
    left_points = list(post.get("left_points") or ["Fragile", "Costly", "Slow"])[:3]
    right_points = list(post.get("right_points") or ["Reusable", "Faster", "Scalable"])[:3]

    for box, label, points, color in (
        (left, left_label, left_points, HUD["muted"]),
        (right, right_label, right_points, HUD["lime"]),
    ):
        cx = (box[0] + box[2]) // 2
        tw = d.textlength(str(label)[:28], font=fonts["h2"])
        d.text((cx - tw / 2, box[1] + 40), str(label)[:28], font=fonts["h2"], fill=color)
        yy = box[1] + 140
        for p in points:
            d.rounded_rectangle([box[0] + 30, yy, box[2] - 30, yy + 90], radius=14, fill=HUD["card"], outline=color, width=1)
            for j, line in enumerate(_wrap(str(p), fonts["body"], box[2] - box[0] - 90, d)[:2]):
                d.text((box[0] + 50, yy + 24 + j * 28), line, font=fonts["body"], fill=HUD["ink"])
            yy += 120

    cta = (post.get("cta") or "Choose the architecture that scales.").strip()
    img = _glow_rect(img, (36, HEIGHT - 120, WIDTH - 36, HEIGHT - 50), HUD["lime"], 16)
    d = ImageDraw.Draw(img)
    d.text((60, HEIGHT - 98), cta[:64], font=fonts["h3"], fill=HUD["ink"])
    return img


def _layout_hud_points(post: dict[str, Any], fonts: dict[str, Any]) -> Any:
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (WIDTH, HEIGHT))
    _gradient(img, HUD["bg"], HUD["bg2"])
    img = _grid(img)
    d = ImageDraw.Draw(img)

    d.text((40, 40), "INTEROP BRIEF", font=fonts["tiny"], fill=HUD["cyan"])
    alert = (post.get("alert_label") or "KEY INSIGHTS").upper()
    img = _glow_rect(img, (36, 90, 280, 138), HUD["lime"], 16)
    d = ImageDraw.Draw(img)
    d.text((56, 102), alert[:22], font=fonts["small"], fill=HUD["lime"])

    title = (post.get("image_title") or post.get("hook") or "FHIR Interoperability").strip()
    y = 170
    for line in _wrap(title, fonts["hero"], WIDTH - 80, d)[:3]:
        d.text((36, y), line, font=fonts["hero"], fill=HUD["ink"])
        y += 62
    sub = (post.get("highlight") or post.get("image_subtitle") or "").strip()
    if sub:
        for line in _wrap(sub, fonts["h2"], WIDTH - 80, d)[:2]:
            d.text((36, y), line, font=fonts["h2"], fill=HUD["lime"])
            y += 42

    bullets = list(post.get("bullets") or ["Point one", "Point two", "Point three", "Point four"])[:4]
    kinds = ["data", "flow", "link", "test"]
    y += 30
    for i, b in enumerate(bullets):
        box = (36, y, WIDTH - 36, y + 150)
        img = _glow_rect(img, box, HUD["cyan"] if i % 2 else HUD["lime"], 18)
        d = ImageDraw.Draw(img)
        _icon_box(d, (60, y + 55), kinds[i % 4], 40)
        d.text((120, y + 28), f"{i + 1:02d}", font=fonts["h2"], fill=HUD["lime"])
        ty = y + 70
        for line in _wrap(str(b), fonts["h3"], WIDTH - 200, d)[:2]:
            d.text((120, ty), line, font=fonts["h3"], fill=HUD["ink"])
            ty += 34
        y += 170

    cta = (post.get("cta") or "Standards create the contract. Delivery creates outcomes.").strip()
    img = _glow_rect(img, (36, HEIGHT - 120, WIDTH - 36, HEIGHT - 50), HUD["lime"], 16)
    d = ImageDraw.Draw(img)
    d.text((60, HEIGHT - 98), cta[:70], font=fonts["h3"], fill=HUD["ink"])
    return img


LAYOUTS = {
    "hud_alert": _layout_hud_alert,
    "dark_tech": _layout_hud_alert,
    "hud_split": _layout_hud_split,
    "split_compare": _layout_hud_split,
    "hud_points": _layout_hud_points,
    "key_points": _layout_hud_points,
    "before_after": _layout_hud_alert,
    "workflow": _layout_hud_alert,
    "title_network": _layout_hud_points,
}


def _enrich(post: dict[str, Any]) -> dict[str, Any]:
    p = dict(post)
    layout = (p.get("image_layout") or "hud_alert").lower()
    if layout not in LAYOUTS:
        layout = "hud_alert"
    p["image_layout"] = layout
    p.setdefault("alert_label", "DON'T DELAY")
    p.setdefault("cta", "The deadline is closer than it looks. Start now.")
    p.setdefault(
        "rail_labels",
        ["Patient Overview", "Interoperability", "Document Exchange"],
    )
    return p


def create_post_image(post: dict[str, Any], out_path: Path) -> Path:
    from PIL import Image

    global WIDTH, HEIGHT

    post = _enrich(post)
    layout = post["image_layout"]

    # Draw at final LinkedIn size (coordinates + fonts stay in sync)
    WIDTH, HEIGHT = 1080, 1350
    fonts = _fonts(scale=1)

    img = LAYOUTS[layout](post, fonts)
    if img.mode != "RGB":
        img = img.convert("RGB")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, format="PNG", compress_level=4)
    print(f"[image] HUD '{layout}' saved: {out_path.name}")
    return out_path
