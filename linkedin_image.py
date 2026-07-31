"""LinkedIn infographic images (1200x1200) — style matched to Health IT posts.

Layouts: split_compare, title_network, before_after, key_points, workflow, dark_tech.
Never draws the author's name.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

WIDTH = 1200
HEIGHT = 1200

THEMES = {
    "blue": {
        "bg": (245, 248, 252),
        "bg2": (230, 240, 250),
        "ink": (20, 40, 80),
        "muted": (90, 110, 140),
        "accent": (37, 99, 235),
        "accent2": (59, 130, 246),
        "card": (255, 255, 255),
        "line": (180, 200, 230),
    },
    "teal": {
        "bg": (244, 250, 250),
        "bg2": (220, 240, 240),
        "ink": (15, 50, 55),
        "muted": (70, 110, 115),
        "accent": (13, 148, 136),
        "accent2": (45, 212, 191),
        "card": (255, 255, 255),
        "line": (170, 210, 205),
    },
    "green_split": {
        "bg": (248, 250, 252),
        "left_bg": (75, 85, 99),
        "right_bg": (22, 163, 74),
        "ink": (255, 255, 255),
        "muted": (220, 220, 220),
        "accent": (255, 255, 255),
        "card": (255, 255, 255),
    },
    "dark_green": {
        "bg": (10, 14, 18),
        "bg2": (18, 28, 24),
        "ink": (236, 253, 245),
        "muted": (134, 180, 160),
        "accent": (52, 211, 153),
        "accent2": (16, 185, 129),
        "card": (24, 36, 32),
        "line": (40, 70, 55),
    },
    "navy": {
        "bg": (15, 23, 42),
        "bg2": (30, 41, 59),
        "ink": (248, 250, 252),
        "muted": (148, 163, 184),
        "accent": (96, 165, 250),
        "accent2": (59, 130, 246),
        "card": (30, 41, 59),
        "line": (51, 65, 85),
    },
}


def _fonts() -> dict[str, Any]:
    from PIL import ImageFont

    bold = next(
        (
            p
            for p in (
                r"C:\Windows\Fonts\segoeuib.ttf",
                r"C:\Windows\Fonts\arialbd.ttf",
                r"C:\Windows\Fonts\calibrib.ttf",
            )
            if Path(p).exists()
        ),
        None,
    )
    regular = next(
        (
            p
            for p in (
                r"C:\Windows\Fonts\segoeui.ttf",
                r"C:\Windows\Fonts\arial.ttf",
                r"C:\Windows\Fonts\calibri.ttf",
            )
            if Path(p).exists()
        ),
        None,
    )
    italic = next(
        (
            p
            for p in (
                r"C:\Windows\Fonts\segoeuiz.ttf",
                r"C:\Windows\Fonts\ariali.ttf",
                r"C:\Windows\Fonts\calibrii.ttf",
            )
            if Path(p).exists()
        ),
        None,
    )
    if not bold or not regular:
        d = ImageFont.load_default()
        return {k: d for k in ("hero", "title", "sub", "label", "body", "small", "italic")}
    return {
        "hero": ImageFont.truetype(bold, 72),
        "title": ImageFont.truetype(bold, 52),
        "sub": ImageFont.truetype(regular, 28),
        "label": ImageFont.truetype(bold, 30),
        "body": ImageFont.truetype(regular, 24),
        "small": ImageFont.truetype(regular, 20),
        "italic": ImageFont.truetype(italic or bold, 64),
    }


def _wrap(text: str, font: Any, max_width: int, draw: Any) -> list[str]:
    words = (text or "").split()
    if not words:
        return []
    lines: list[str] = []
    cur = words[0]
    for w in words[1:]:
        trial = f"{cur} {w}"
        if draw.textlength(trial, font=font) <= max_width:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def _seed(post: dict[str, Any]) -> int:
    key = f"{post.get('topic')}|{post.get('image_title')}|{post.get('image_layout')}"
    return int(hashlib.md5(key.encode()).hexdigest()[:8], 16)


def _theme(post: dict[str, Any]) -> dict[str, Any]:
    name = (post.get("accent_theme") or "blue").lower()
    if name not in THEMES:
        name = list(THEMES.keys())[_seed(post) % len(THEMES)]
    return THEMES[name]


def _layout(post: dict[str, Any]) -> str:
    layout = (post.get("image_layout") or "").strip().lower()
    allowed = {"split_compare", "title_network", "before_after", "key_points", "workflow", "dark_tech"}
    if layout in allowed:
        return layout
    # Heuristic from topic/hook
    t = f"{post.get('topic', '')} {post.get('hook', '')}".lower()
    if " vs " in t or "versus" in t or "hl7" in t and "fhir" in t:
        return "split_compare"
    if "before" in t or "after" in t or "modern" in t:
        return "before_after"
    if "pas" in t or "bundle" in t or "crd" in t or "dtr" in t:
        return "dark_tech"
    if "workflow" in t or "step" in t or "how" in t:
        return "workflow"
    if "cms" in t or "0057" in t or "patient access" in t:
        return "key_points"
    return "title_network"


def _title(post: dict[str, Any]) -> str:
    return (post.get("image_title") or post.get("hook") or post.get("topic") or "Healthcare Interoperability").strip()


def _subtitle(post: dict[str, Any]) -> str:
    return (post.get("image_subtitle") or "").strip()


def _draw_network_bg(draw: Any, theme: dict[str, Any], dark: bool = False) -> None:
    import random

    rng = random.Random(42)
    w, h = WIDTH, HEIGHT
    # soft dots + faint edges
    nodes = [(rng.randint(40, w - 40), rng.randint(40, h - 40)) for _ in range(28)]
    line = theme.get("line", (200, 210, 230))
    accent = theme["accent"]
    for i, (x, y) in enumerate(nodes):
        r = 3 if i % 3 else 5
        color = accent if i % 5 == 0 else line
        draw.ellipse([x - r, y - r, x + r, y + r], fill=color)
        if i:
            px, py = nodes[i - 1]
            if abs(px - x) + abs(py - y) < 380:
                draw.line([(px, py), (x, y)], fill=line, width=1)
    # decorative circles
    for cx, cy, rad in [(180, 160, 90), (1000, 220, 120), (960, 980, 140), (200, 1000, 80)]:
        draw.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], outline=line, width=2)


def _icon_circle(draw: Any, xy: tuple[int, int], color: tuple[int, int, int], kind: str = "node") -> None:
    x, y = xy
    draw.ellipse([x - 36, y - 36, x + 36, y + 36], fill=color)
    # simple white glyph
    white = (255, 255, 255)
    if kind == "chain":
        draw.arc([x - 18, y - 10, x - 2, y + 10], 0, 360, fill=white, width=3)
        draw.arc([x + 2, y - 10, x + 18, y + 10], 0, 360, fill=white, width=3)
    elif kind == "rocket":
        draw.polygon([(x, y - 18), (x + 14, y + 12), (x - 14, y + 12)], fill=white)
    elif kind == "server":
        draw.rectangle([x - 16, y - 18, x + 16, y + 18], outline=white, width=3)
        draw.line([(x - 10, y - 6), (x + 10, y - 6)], fill=white, width=2)
        draw.line([(x - 10, y + 6), (x + 10, y + 6)], fill=white, width=2)
    elif kind == "cloud":
        draw.ellipse([x - 20, y - 8, x + 8, y + 16], fill=white)
        draw.ellipse([x - 8, y - 16, x + 20, y + 10], fill=white)
    elif kind == "check":
        draw.line([(x - 12, y), (x - 2, y + 12), (x + 14, y - 12)], fill=white, width=4)
    else:
        draw.ellipse([x - 8, y - 8, x + 8, y + 8], fill=white)


def _layout_split_compare(img: Any, draw: Any, fonts: dict[str, Any], post: dict[str, Any], theme: dict[str, Any]) -> None:
    left_bg = theme.get("left_bg", (75, 85, 99))
    right_bg = theme.get("right_bg", (22, 163, 74))
    # If theme isn't green_split, invent contrast colors
    if "left_bg" not in theme:
        left_bg = (71, 85, 105)
        right_bg = theme["accent"]

    mid = WIDTH // 2
    draw.rectangle([0, 0, mid, HEIGHT], fill=left_bg)
    draw.rectangle([mid, 0, WIDTH, HEIGHT], fill=right_bg)

    left_label = post.get("left_label") or "Before"
    right_label = post.get("right_label") or "After"
    left_points = list(post.get("left_points") or ["Manual effort", "Fragile integrations", "Operational tax"])[:3]
    right_points = list(post.get("right_points") or ["API-first", "Reusable contracts", "Growth engine"])[:3]

    _icon_circle(draw, (mid // 2, 280), (55, 65, 80), "chain")
    _icon_circle(draw, (mid + mid // 2, 280), tuple(min(255, c + 30) for c in right_bg[:3]), "rocket")

    for label, cx, points in (
        (left_label, mid // 2, left_points),
        (right_label, mid + mid // 2, right_points),
    ):
        lines = _wrap(str(label), fonts["label"], 480, draw)[:3]
        y = 400
        for line in lines:
            tw = draw.textlength(line, font=fonts["label"])
            draw.text((cx - tw / 2, y), line, font=fonts["label"], fill=(255, 255, 255))
            y += 40
        y += 30
        for p in points:
            plines = _wrap(f"• {p}", fonts["body"], 480, draw)[:2]
            for pl in plines:
                tw = draw.textlength(pl, font=fonts["body"])
                draw.text((cx - tw / 2, y), pl, font=fonts["body"], fill=(240, 240, 240))
                y += 32
            y += 8

    # tiny footer tags — no name
    draw.text((40, HEIGHT - 60), "#FHIR  #Interoperability", font=fonts["small"], fill=(230, 230, 230))


def _layout_title_network(img: Any, draw: Any, fonts: dict[str, Any], post: dict[str, Any], theme: dict[str, Any]) -> None:
    # gradient-ish bg
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(theme["bg"][0] * (1 - ratio) + theme["bg2"][0] * ratio)
        g = int(theme["bg"][1] * (1 - ratio) + theme["bg2"][1] * ratio)
        b = int(theme["bg"][2] * (1 - ratio) + theme["bg2"][2] * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))
    _draw_network_bg(draw, theme)

    # floating mini cards
    cards = [
        (80, 120, post.get("left_label") or "FHIR"),
        (920, 160, post.get("right_label") or "CMS"),
        (100, 920, "API"),
        (880, 880, "Data"),
    ]
    for x, y, label in cards:
        draw.rounded_rectangle([x, y, x + 160, y + 90], radius=16, fill=theme["card"], outline=theme["line"], width=2)
        tw = draw.textlength(str(label)[:12], font=fonts["body"])
        draw.text((x + 80 - tw / 2, y + 28), str(label)[:12], font=fonts["body"], fill=theme["accent"])

    title = _title(post)
    # Emphasize mid words if "From X to Y" pattern
    lines = _wrap(title, fonts["hero"], 980, draw)[:3]
    total_h = len(lines) * 88
    y = (HEIGHT - total_h) // 2 - 20
    for line in lines:
        tw = draw.textlength(line, font=fonts["hero"])
        # color alternating: ink / accent for visual punch
        draw.text(((WIDTH - tw) / 2, y), line, font=fonts["italic"], fill=theme["accent"] if len(line) < 18 else theme["ink"])
        y += 88

    sub = _subtitle(post)
    if sub:
        for line in _wrap(sub, fonts["sub"], 900, draw)[:2]:
            tw = draw.textlength(line, font=fonts["sub"])
            draw.text(((WIDTH - tw) / 2, y + 20), line, font=fonts["sub"], fill=theme["muted"])
            y += 36


def _layout_before_after(img: Any, draw: Any, fonts: dict[str, Any], post: dict[str, Any], theme: dict[str, Any]) -> None:
    draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(255, 255, 255))
    title = _title(post)
    for i, line in enumerate(_wrap(title, fonts["title"], 1000, draw)[:2]):
        tw = draw.textlength(line, font=fonts["title"])
        draw.text(((WIDTH - tw) / 2, 80 + i * 60), line, font=fonts["title"], fill=theme["ink"])

    steps = list(post.get("steps") or ["Before FHIR", "FHIR", "After FHIR"])[:3]
    while len(steps) < 3:
        steps.append("")
    xs = [220, 600, 980]
    kinds = ["server", "node", "cloud"]
    colors = [(148, 163, 184), theme["accent"], (20, 184, 166)]
    for i, (x, label, kind, color) in enumerate(zip(xs, steps, kinds, colors)):
        _icon_circle(draw, (x, 520), color, kind)
        for j, line in enumerate(_wrap(str(label), fonts["label"], 280, draw)[:2]):
            tw = draw.textlength(line, font=fonts["label"])
            draw.text((x - tw / 2, 620 + j * 36), line, font=fonts["label"], fill=theme["ink"])
        if i < 2:
            draw.polygon([(x + 70, 510), (x + 110, 520), (x + 70, 530)], fill=colors[i + 1])

    sub = _subtitle(post) or "Data movement. Solved."
    for j, line in enumerate(_wrap(sub, fonts["sub"], 900, draw)[:2]):
        tw = draw.textlength(line, font=fonts["sub"])
        draw.text(((WIDTH - tw) / 2, 900 + j * 36), line, font=fonts["sub"], fill=theme["muted"])


def _layout_key_points(img: Any, draw: Any, fonts: dict[str, Any], post: dict[str, Any], theme: dict[str, Any]) -> None:
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(theme["bg"][0] * (1 - ratio) + theme["bg2"][0] * ratio)
        g = int(theme["bg"][1] * (1 - ratio) + theme["bg2"][1] * ratio)
        b = int(theme["bg"][2] * (1 - ratio) + theme["bg2"][2] * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # header bar
    draw.rectangle([0, 0, WIDTH, 220], fill=(30, 64, 175))
    title = _title(post)
    y = 50
    for line in _wrap(title, fonts["title"], 1080, draw)[:2]:
        draw.text((50, y), line, font=fonts["title"], fill=(255, 255, 255))
        y += 58
    sub = _subtitle(post)
    if sub:
        draw.text((50, 160), sub[:80], font=fonts["small"], fill=(200, 220, 255))

    bullets = list(post.get("bullets") or post.get("steps") or [
        "Standards create the contract",
        "Data quality decides adoption",
        "Operating model beats demos",
    ])[:5]

    colors = [(34, 197, 94), (249, 115, 22), (59, 130, 246), (239, 68, 68), (168, 85, 247)]
    top = 260
    card_h = min(150, (HEIGHT - top - 80) // max(len(bullets), 1) - 16)
    for i, bullet in enumerate(bullets):
        y0 = top + i * (card_h + 16)
        draw.rounded_rectangle([50, y0, WIDTH - 50, y0 + card_h], radius=18, fill=(255, 255, 255), outline=theme.get("line", (220, 220, 220)), width=2)
        draw.rounded_rectangle([50, y0, 70, y0 + card_h], radius=8, fill=colors[i % len(colors)])
        num = str(i + 1)
        draw.text((95, y0 + 24), num, font=fonts["label"], fill=colors[i % len(colors)])
        ty = y0 + 28
        for line in _wrap(str(bullet), fonts["body"], 980, draw)[:3]:
            draw.text((140, ty), line, font=fonts["body"], fill=(30, 40, 60))
            ty += 30


def _layout_workflow(img: Any, draw: Any, fonts: dict[str, Any], post: dict[str, Any], theme: dict[str, Any]) -> None:
    draw.rectangle([0, 0, WIDTH, HEIGHT], fill=theme["bg"] if theme["ink"][0] < 100 else (248, 250, 252))
    # dark header strip
    draw.rectangle([0, 0, WIDTH, 200], fill=(88, 28, 135))
    title = _title(post)
    y = 50
    for line in _wrap(title, fonts["title"], 1100, draw)[:2]:
        draw.text((40, y), line, font=fonts["title"], fill=(255, 255, 255))
        y += 55
    sub = _subtitle(post)
    if sub:
        draw.text((40, 150), sub[:90], font=fonts["small"], fill=(230, 210, 255))

    steps = list(post.get("steps") or ["Request", "API", "Validate", "Decide", "Respond"])[:6]
    n = len(steps)
    gap = 28
    usable = WIDTH - 80
    card_w = (usable - gap * (n - 1)) // n
    y0 = 320
    for i, step in enumerate(steps):
        x0 = 40 + i * (card_w + gap)
        draw.rounded_rectangle([x0, y0, x0 + card_w, y0 + 420], radius=16, fill=(255, 255, 255), outline=(220, 200, 240), width=2)
        _icon_circle(draw, (x0 + card_w // 2, y0 + 90), theme["accent"] if i % 2 == 0 else (168, 85, 247), "check" if i == n - 1 else "node")
        draw.text((x0 + 16, y0 + 160), f"STEP {i + 1}", font=fonts["small"], fill=theme["accent"])
        ty = y0 + 200
        for line in _wrap(str(step), fonts["body"], card_w - 30, draw)[:5]:
            draw.text((x0 + 16, ty), line, font=fonts["body"], fill=(30, 30, 50))
            ty += 32
        if i < n - 1:
            draw.polygon(
                [(x0 + card_w + 4, y0 + 200), (x0 + card_w + gap - 4, y0 + 210), (x0 + card_w + 4, y0 + 220)],
                fill=(168, 85, 247),
            )


def _layout_dark_tech(img: Any, draw: Any, fonts: dict[str, Any], post: dict[str, Any], theme: dict[str, Any]) -> None:
    # force dark theme colors
    theme = THEMES["dark_green"]
    draw.rectangle([0, 0, WIDTH, HEIGHT], fill=theme["bg"])
    for y in range(HEIGHT):
        if y % 40 == 0:
            draw.line([(0, y), (WIDTH, y)], fill=theme["line"], width=1)

    title = _title(post)
    y = 60
    for line in _wrap(title, fonts["title"], 1100, draw)[:3]:
        draw.text((50, y), line, font=fonts["title"], fill=theme["accent"])
        y += 58
    sub = _subtitle(post)
    if sub:
        for line in _wrap(sub, fonts["sub"], 1050, draw)[:2]:
            draw.text((50, y + 10), line, font=fonts["sub"], fill=theme["muted"])
            y += 34

    bullets = list(post.get("bullets") or post.get("steps") or [
        "Claim — administrative backbone",
        "ServiceRequest — clinical intent",
        "Coverage — enrollment link",
        "Practitioner & Organization — actors",
    ])[:5]

    # left list
    y0 = y + 60
    for i, b in enumerate(bullets):
        yy = y0 + i * 130
        draw.rounded_rectangle([50, yy, 700, yy + 110], radius=14, outline=theme["accent"], width=2)
        draw.ellipse([70, yy + 35, 100, yy + 65], fill=theme["accent"])
        draw.text((78, yy + 38), str(i + 1), font=fonts["small"], fill=(10, 14, 18))
        ty = yy + 28
        for line in _wrap(str(b), fonts["body"], 560, draw)[:2]:
            draw.text((120, ty), line, font=fonts["body"], fill=theme["ink"])
            ty += 30

    # right hub
    cx, cy = 960, 700
    draw.ellipse([cx - 110, cy - 110, cx + 110, cy + 110], outline=theme["accent"], width=3)
    hub = "PAS" if "pas" in _title(post).lower() else "FHIR"
    tw = draw.textlength(hub, font=fonts["label"])
    draw.text((cx - tw / 2, cy - 16), hub, font=fonts["label"], fill=theme["accent"])
    for i, ang_pos in enumerate([(960, 480), (1120, 620), (1100, 860), (820, 860), (800, 620)]):
        x, y = ang_pos
        draw.line([(cx, cy), (x, y)], fill=theme["accent2"], width=2)
        draw.ellipse([x - 18, y - 18, x + 18, y + 18], fill=theme["accent2"])


LAYOUTS = {
    "split_compare": _layout_split_compare,
    "title_network": _layout_title_network,
    "before_after": _layout_before_after,
    "key_points": _layout_key_points,
    "workflow": _layout_workflow,
    "dark_tech": _layout_dark_tech,
}


def _enrich_defaults(post: dict[str, Any]) -> dict[str, Any]:
    """Fill visual fields when AI/fallback omitted them."""
    p = dict(post)
    layout = _layout(p)
    p["image_layout"] = layout
    topic = p.get("topic") or "FHIR interoperability"
    hook = p.get("hook") or topic

    if not p.get("image_title"):
        p["image_title"] = hook if len(hook) <= 60 else topic[:60]
    if not p.get("accent_theme"):
        p["accent_theme"] = {
            "split_compare": "green_split",
            "title_network": "blue",
            "before_after": "teal",
            "key_points": "blue",
            "workflow": "blue",
            "dark_tech": "dark_green",
        }.get(layout, "blue")

    if layout == "split_compare":
        p.setdefault("left_label", "HL7 v2: Operational Tax")
        p.setdefault("right_label", "FHIR: Growth Engine")
        p.setdefault("left_points", ["Point-to-point fragility", "High maintenance cost", "Hard to scale partners"])
        p.setdefault("right_points", ["Reusable APIs", "Faster partner onboarding", "Productizable data access"])
    elif layout == "before_after":
        p.setdefault("steps", ["Before FHIR", "FHIR", "After FHIR"])
        p.setdefault("image_subtitle", "Data movement. Solved.")
    elif layout == "workflow":
        p.setdefault("steps", ["Initiate", "Send via FHIR", "Validate", "Decide", "Respond"])
    elif layout in ("key_points", "dark_tech"):
        p.setdefault(
            "bullets",
            [
                "Clean profiles beat one-off extensions",
                "Directory quality is an ownership problem",
                "Prior Auth APIs need boring reliability",
                "Test negative paths before go-live",
            ],
        )
    return p


def create_post_image(post: dict[str, Any], out_path: Path) -> Path:
    from PIL import Image, ImageDraw

    post = _enrich_defaults(post)
    layout = post["image_layout"]
    theme = _theme(post)
    # split_compare prefers green_split palette
    if layout == "split_compare":
        theme = THEMES["green_split"]
    elif layout == "dark_tech":
        theme = THEMES["dark_green"]

    img = Image.new("RGB", (WIDTH, HEIGHT), theme.get("bg", (255, 255, 255)))
    draw = ImageDraw.Draw(img)
    fonts = _fonts()
    LAYOUTS.get(layout, _layout_title_network)(img, draw, fonts, post, theme)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, format="PNG", optimize=True)
    print(f"[image] Infographic '{layout}' saved: {out_path.name}")
    return out_path


def image_path_for_draft(draft_md: Path) -> Path:
    return draft_md.with_suffix(".png")
