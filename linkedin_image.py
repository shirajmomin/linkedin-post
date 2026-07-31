"""Premium LinkedIn HUD / HealthTech visuals (1080x1350).

Primary style matches high-end dark neon HealthTech posts:
- dark canvas + grid
- neon lime / cyan accents
- alert chip, big headline, highlight line
- icon bullets + optional medical wireframe panel
- bottom CTA bar

No author name on the image.
"""

from __future__ import annotations

import hashlib
import io
import math
import random
import urllib.parse
import urllib.request
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

ASSETS = Path(__file__).resolve().parent / "assets"
ASSETS.mkdir(exist_ok=True)


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


def _download(url: str, timeout: int = 90) -> bytes | None:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "LinkedInPostAgent/2.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except Exception as exc:  # noqa: BLE001
        print(f"[image] download failed: {exc}")
        return None


def _wireframe_asset(seed: int) -> Any | None:
    """Fetch / cache a neon medical wireframe visual (no text)."""
    from PIL import Image

    cache = ASSETS / f"wireframe_{seed % 7}.png"
    if cache.exists() and cache.stat().st_size > 8000:
        try:
            return Image.open(cache).convert("RGBA")
        except Exception:
            pass

    prompt = (
        "futuristic medical HUD, glowing cyan wireframe human skeleton and nervous system, "
        "dark charcoal background, digital xray scan style, neon blue edges, high detail, "
        "no text, no letters, no logo, no watermark, centered figure"
    )
    encoded = urllib.parse.quote(prompt)
    url = (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width=768&height=1200&seed={seed % 9973}&nologo=true&model=flux"
    )
    print("[image] Fetching HUD wireframe visual…")
    raw = _download(url, timeout=120)
    if not raw:
        return None
    try:
        img = Image.open(io.BytesIO(raw)).convert("RGBA")
        img.save(cache, format="PNG")
        return img
    except Exception as exc:  # noqa: BLE001
        print(f"[image] wireframe decode failed: {exc}")
        return None


def _gradient(img: Any, c1: tuple[int, int, int], c2: tuple[int, int, int]) -> None:
    from PIL import ImageDraw

    d = ImageDraw.Draw(img)
    for y in range(HEIGHT):
        t = y / max(HEIGHT - 1, 1)
        r = int(c1[0] + (c2[0] - c1[0]) * t)
        g = int(c1[1] + (c2[1] - c1[1]) * t)
        b = int(c1[2] + (c2[2] - c1[2]) * t)
        d.line([(0, y), (WIDTH, y)], fill=(r, g, b))


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


def _draw_fallback_figure(base: Any, box: tuple[int, int, int, int]) -> Any:
    """Geometric neon 'scan figure' if AI wireframe unavailable."""
    from PIL import Image, ImageDraw, ImageFilter

    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    x0, y0, x1, y1 = box
    cx = (x0 + x1) // 2
    # outer glow frame
    d.rounded_rectangle([x0, y0, x1, y1], radius=24, outline=(*HUD["cyan"], 80), width=2)
    # head
    d.ellipse([cx - 50, y0 + 40, cx + 50, y0 + 140], outline=HUD["cyan"], width=3)
    # spine
    d.line([(cx, y0 + 140), (cx, y1 - 120)], fill=HUD["lime"], width=3)
    # ribs
    for i in range(6):
        yy = y0 + 180 + i * 28
        w = 70 + i * 4
        d.arc([cx - w, yy - 20, cx + w, yy + 20], 200, 340, fill=HUD["cyan"], width=2)
    # arms
    d.line([(cx, y0 + 200), (cx - 110, y0 + 320)], fill=HUD["cyan"], width=3)
    d.line([(cx, y0 + 200), (cx + 110, y0 + 320)], fill=HUD["cyan"], width=3)
    # pelvis + legs
    d.polygon([(cx - 55, y1 - 280), (cx + 55, y1 - 280), (cx + 40, y1 - 240), (cx - 40, y1 - 240)], outline=HUD["lime"], width=2)
    d.line([(cx - 25, y1 - 240), (cx - 45, y1 - 80)], fill=HUD["cyan"], width=3)
    d.line([(cx + 25, y1 - 240), (cx + 45, y1 - 80)], fill=HUD["cyan"], width=3)
    # scan nodes
    for px, py in [(cx, y0 + 90), (cx - 40, y0 + 220), (cx + 40, y0 + 220), (cx, y1 - 260), (cx - 45, y1 - 120)]:
        d.ellipse([px - 5, py - 5, px + 5, py + 5], fill=HUD["lime"])
    # horizontal scan line
    midy = (y0 + y1) // 2
    d.line([(x0 + 20, midy), (x1 - 20, midy)], fill=(*HUD["lime"], 120), width=2)
    overlay = overlay.filter(ImageFilter.GaussianBlur(0.6))
    return Image.alpha_composite(base.convert("RGBA"), overlay)


def _compose_wireframe(base: Any, box: tuple[int, int, int, int], seed: int) -> Any:
    from PIL import Image, ImageEnhance

    fig = _wireframe_asset(seed)
    x0, y0, x1, y1 = box
    bw, bh = x1 - x0, y1 - y0
    if fig is None:
        return _draw_fallback_figure(base, box)

    fig = fig.resize((bw, bh), Image.Resampling.LANCZOS)
    # darken + boost cyan feel
    fig = ImageEnhance.Brightness(fig).enhance(0.85)
    fig = ImageEnhance.Contrast(fig).enhance(1.25)
    # soft round mask
    mask = Image.new("L", (bw, bh), 0)
    from PIL import ImageDraw

    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([0, 0, bw, bh], radius=28, fill=220)
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    layer.paste(fig, (x0, y0), mask)
    # neon frame
    framed = Image.new("RGBA", base.size, (0, 0, 0, 0))
    fd = ImageDraw.Draw(framed)
    fd.rounded_rectangle([x0 - 2, y0 - 2, x1 + 2, y1 + 2], radius=30, outline=(*HUD["cyan"], 160), width=2)
    out = Image.alpha_composite(base.convert("RGBA"), layer)
    out = Image.alpha_composite(out, framed)
    return out


def _layout_hud_alert(post: dict[str, Any], fonts: dict[str, Any]) -> Any:
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (WIDTH, HEIGHT))
    _gradient(img, HUD["bg"], HUD["bg2"])
    img = _grid(img)

    # Left content width vs right figure
    left_w = 620
    fig_box = (650, 220, WIDTH - 36, HEIGHT - 210)

    img = _compose_wireframe(img, fig_box, _seed(post))
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
        # supporting line under date
        support = (post.get("support_line") or "Is around the corner — start preparing now.").strip()
        for line in _wrap(support, fonts["body"], left_w - 40, d)[:2]:
            d.text((36, y), line, font=fonts["body"], fill=HUD["cyan"])
            y += 30

    # Intro
    intro = (post.get("intro") or "").strip()
    if not intro:
        intro = (post.get("image_subtitle") or "Electronic prior authorization is no longer optional for impacted payers.")[:140]
    y += 8
    for line in _wrap(intro, fonts["body"], left_w - 50, d)[:3]:
        d.text((36, y), line, font=fonts["body"], fill=HUD["muted"])
        y += 30

    # Bullets with neon icon boxes
    bullets = list(post.get("bullets") or [])[:4]
    if not bullets:
        bullets = [
            "Prior Auth APIs must be production-ready",
            "CRD / DTR / PAS need end-to-end testing",
            "Directory + clinical context must connect",
            "Late testing creates go-live risk",
        ]
    kinds = ["data", "flow", "link", "test"]
    y += 28
    for i, b in enumerate(bullets):
        _icon_box(d, (36, y), kinds[i % 4], 36)
        ty = y + 4
        for line in _wrap(str(b), fonts["body"], left_w - 100, d)[:2]:
            d.text((88, ty), line, font=fonts["body"], fill=HUD["ink"])
            ty += 28
        y = max(y + 56, ty + 12)

    # Right rail labels
    rails = list(post.get("rail_labels") or ["Patient Overview", "Interoperability", "Document Exchange"])[:3]
    rail_icons = ["patient", "link", "doc"]
    ry = 260
    for i, label in enumerate(rails):
        rx = WIDTH - 52
        # vertical-ish stacked labels on far right of figure
        box = (rx - 150, ry, rx, ry + 120)
        d.rounded_rectangle(box, radius=12, outline=HUD["lime"], width=2)
        _icon_box(d, (rx - 118, ry + 18), rail_icons[i % 3], 28)
        # wrap label under icon
        ly = ry + 58
        for line in _wrap(str(label), fonts["tiny"], 130, d)[:2]:
            tw = d.textlength(line, font=fonts["tiny"])
            d.text((rx - 75 - tw / 2, ly), line, font=fonts["tiny"], fill=HUD["ink"])
            ly += 20
        ry += 150

    # CTA bar
    cta = (post.get("cta") or "The deadline is closer than it looks. Start now.").strip()
    cta_box = (36, HEIGHT - 150, WIDTH - 36, HEIGHT - 78)
    img = _glow_rect(img, cta_box, HUD["lime"], radius=18)
    d = ImageDraw.Draw(img)
    _icon_box(d, (58, HEIGHT - 132), "clock", 34)
    d.text((110, HEIGHT - 128), cta[:70], font=fonts["h3"], fill=HUD["ink"])

    # Footer note
    foot = (post.get("footer_note") or "Build · Test · Validate FHIR prior-auth workflows before the deadline.")[:90]
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

    scale = 2
    out_w, out_h = 1080, 1350
    WIDTH, HEIGHT = out_w * scale, out_h * scale
    fonts = _fonts(scale=scale)

    img = LAYOUTS[layout](post, fonts)
    if img.mode != "RGB":
        img = img.convert("RGB")
    img = img.resize((out_w, out_h), Image.Resampling.LANCZOS)

    WIDTH, HEIGHT = out_w, out_h
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, format="PNG", compress_level=4)
    print(f"[image] HUD '{layout}' saved: {out_path.name}")
    return out_path


def image_path_for_draft(draft_md: Path) -> Path:
    return draft_md.with_suffix(".png")
