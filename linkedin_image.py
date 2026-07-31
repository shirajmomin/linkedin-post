"""LinkedIn infographic images (1200x1200) — Health IT post style.

Layouts: split_compare, title_network, before_after, key_points, workflow, dark_tech.
Never draws the author's name. Each topic gets a distinct visual.
"""

from __future__ import annotations

import hashlib
import random
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
        "header": (30, 64, 175),
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
        "header": (15, 118, 110),
    },
    "green_split": {
        "bg": (248, 250, 252),
        "left_bg": (75, 85, 99),
        "right_bg": (22, 163, 74),
        "ink": (255, 255, 255),
        "muted": (220, 220, 220),
        "accent": (255, 255, 255),
        "card": (255, 255, 255),
        "line": (200, 200, 200),
        "header": (22, 163, 74),
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
        "header": (6, 78, 59),
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
        "header": (30, 58, 138),
    },
    "orange": {
        "bg": (255, 247, 237),
        "bg2": (254, 215, 170),
        "ink": (67, 20, 7),
        "muted": (154, 52, 18),
        "accent": (234, 88, 12),
        "accent2": (251, 146, 60),
        "card": (255, 255, 255),
        "line": (253, 186, 116),
        "header": (194, 65, 12),
    },
    "purple": {
        "bg": (250, 245, 255),
        "bg2": (237, 233, 254),
        "ink": (46, 16, 101),
        "muted": (91, 33, 182),
        "accent": (124, 58, 237),
        "accent2": (167, 139, 250),
        "card": (255, 255, 255),
        "line": (196, 181, 253),
        "header": (91, 33, 182),
    },
}


def _fonts() -> dict[str, Any]:
    from PIL import ImageFont

    bold_candidates = [
        r"C:\Windows\Fonts\segoeuib.ttf",
        r"C:\Windows\Fonts\arialbd.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ]
    regular_candidates = [
        r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    ]
    italic_candidates = [
        r"C:\Windows\Fonts\segoeuiz.ttf",
        r"C:\Windows\Fonts\ariali.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf",
    ]
    bold = next((p for p in bold_candidates if Path(p).exists()), None)
    regular = next((p for p in regular_candidates if Path(p).exists()), None)
    italic = next((p for p in italic_candidates if Path(p).exists()), None)
    if not bold or not regular:
        d = ImageFont.load_default()
        print("[image] WARNING: no TTF fonts found — install fonts-dejavu-core")
        return {k: d for k in ("hero", "title", "sub", "label", "body", "small", "italic")}
    return {
        "hero": ImageFont.truetype(bold, 64),
        "title": ImageFont.truetype(bold, 48),
        "sub": ImageFont.truetype(regular, 26),
        "label": ImageFont.truetype(bold, 28),
        "body": ImageFont.truetype(regular, 22),
        "small": ImageFont.truetype(regular, 18),
        "italic": ImageFont.truetype(italic or bold, 58),
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
    key = f"{post.get('topic')}|{post.get('image_title')}|{post.get('hook')}|{post.get('image_layout')}"
    return int(hashlib.md5(key.encode()).hexdigest()[:8], 16)


def _theme(post: dict[str, Any]) -> dict[str, Any]:
    name = (post.get("accent_theme") or "").lower()
    if name not in THEMES:
        keys = [k for k in THEMES if k != "green_split"]
        name = keys[_seed(post) % len(keys)]
    return THEMES[name]


def _layout(post: dict[str, Any]) -> str:
    layout = (post.get("image_layout") or "").strip().lower()
    allowed = {"split_compare", "title_network", "before_after", "key_points", "workflow", "dark_tech"}
    if layout in allowed:
        return layout
    layouts = list(allowed)
    return layouts[_seed(post) % len(layouts)]


def _title(post: dict[str, Any]) -> str:
    t = (post.get("image_title") or post.get("hook") or post.get("topic") or "Healthcare Interoperability").strip()
    # Keep titles short so they render large and readable
    words = t.split()
    if len(words) > 8:
        t = " ".join(words[:8])
    return t


def _subtitle(post: dict[str, Any]) -> str:
    return (post.get("image_subtitle") or "").strip()


def _badges(post: dict[str, Any]) -> list[str]:
    badges = list(post.get("badge_labels") or [])
    if len(badges) >= 4:
        return [str(b)[:14] for b in badges[:4]]
    defaults = ["FHIR", "CMS", "API", "Data"]
    # Derive from topic so cards are not always identical
    t = (post.get("topic") or "").lower()
    if "uscdi" in t or "us core" in t:
        defaults = ["USCDI", "US Core", "Must Support", "Consumer"]
    elif "smart" in t:
        defaults = ["SMART", "OAuth", "Launch", "Scopes"]
    elif "ai" in t:
        defaults = ["AI", "FHIR", "Human", "Governance"]
    elif "leadership" in t:
        defaults = ["Risk", "Sequence", "Delivery", "Ownership"]
    elif "medicare" in t:
        defaults = ["Medicare", "Commercial", "FHIR", "Coverage"]
    elif "test" in t:
        defaults = ["Synthetic", "Negative", "Contract", "CI"]
    elif post.get("left_label") or post.get("right_label"):
        defaults = [
            str(post.get("left_label") or "FHIR")[:14],
            str(post.get("right_label") or "CMS")[:14],
            "API",
            "Interop",
        ]
    return defaults


def _draw_network_bg(draw: Any, theme: dict[str, Any], seed: int) -> None:
    rng = random.Random(seed)
    nodes = [(rng.randint(40, WIDTH - 40), rng.randint(40, HEIGHT - 40)) for _ in range(32)]
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
    for _ in range(4):
        cx, cy = rng.randint(100, WIDTH - 100), rng.randint(100, HEIGHT - 100)
        rad = rng.randint(70, 150)
        draw.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], outline=line, width=2)


def _icon_circle(draw: Any, xy: tuple[int, int], color: tuple[int, int, int], kind: str = "node") -> None:
    x, y = xy
    draw.ellipse([x - 36, y - 36, x + 36, y + 36], fill=color)
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

    _icon_circle(draw, (mid // 2, 260), (55, 65, 80), "chain")
    _icon_circle(draw, (mid + mid // 2, 260), tuple(min(255, c + 30) for c in right_bg[:3]), "rocket")

    for label, cx, points in (
        (left_label, mid // 2, left_points),
        (right_label, mid + mid // 2, right_points),
    ):
        lines = _wrap(str(label), fonts["label"], 480, draw)[:3]
        y = 370
        for line in lines:
            tw = draw.textlength(line, font=fonts["label"])
            draw.text((cx - tw / 2, y), line, font=fonts["label"], fill=(255, 255, 255))
            y += 40
        y += 24
        for p in points:
            for pl in _wrap(f"• {p}", fonts["body"], 480, draw)[:2]:
                tw = draw.textlength(pl, font=fonts["body"])
                draw.text((cx - tw / 2, y), pl, font=fonts["body"], fill=(240, 240, 240))
                y += 32
            y += 8

    draw.text((40, HEIGHT - 60), "#FHIR  #Interoperability", font=fonts["small"], fill=(230, 230, 230))


def _layout_title_network(img: Any, draw: Any, fonts: dict[str, Any], post: dict[str, Any], theme: dict[str, Any]) -> None:
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(theme["bg"][0] * (1 - ratio) + theme["bg2"][0] * ratio)
        g = int(theme["bg"][1] * (1 - ratio) + theme["bg2"][1] * ratio)
        b = int(theme["bg"][2] * (1 - ratio) + theme["bg2"][2] * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))
    _draw_network_bg(draw, theme, _seed(post))

    badges = _badges(post)
    positions = [(70, 90), (930, 110), (90, 980), (900, 960)]
    for (x, y), label in zip(positions, badges):
        draw.rounded_rectangle([x, y, x + 180, y + 84], radius=16, fill=theme["card"], outline=theme["accent"], width=3)
        tw = draw.textlength(label, font=fonts["body"])
        draw.text((x + 90 - tw / 2, y + 26), label, font=fonts["body"], fill=theme["accent"])

    # Center title panel for readability
    draw.rounded_rectangle([80, 380, WIDTH - 80, 820], radius=28, fill=(*theme["card"],) if False else theme["card"])
    # soft panel with slight outline
    draw.rounded_rectangle([80, 380, WIDTH - 80, 820], radius=28, outline=theme["line"], width=2)

    title = _title(post)
    lines = _wrap(title, fonts["hero"], 960, draw)[:3]
    y = 460
    for line in lines:
        tw = draw.textlength(line, font=fonts["hero"])
        draw.text(((WIDTH - tw) / 2, y), line, font=fonts["hero"], fill=theme["ink"])
        y += 78

    sub = _subtitle(post)
    if sub:
        for line in _wrap(sub, fonts["sub"], 900, draw)[:2]:
            tw = draw.textlength(line, font=fonts["sub"])
            draw.text(((WIDTH - tw) / 2, y + 16), line, font=fonts["sub"], fill=theme["muted"])
            y += 36


def _layout_before_after(img: Any, draw: Any, fonts: dict[str, Any], post: dict[str, Any], theme: dict[str, Any]) -> None:
    draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(255, 255, 255))
    draw.rectangle([0, 0, WIDTH, 16], fill=theme["accent"])
    title = _title(post)
    for i, line in enumerate(_wrap(title, fonts["title"], 1000, draw)[:2]):
        tw = draw.textlength(line, font=fonts["title"])
        draw.text(((WIDTH - tw) / 2, 80 + i * 58), line, font=fonts["title"], fill=theme["ink"])

    steps = list(post.get("steps") or ["Before FHIR", "FHIR", "After FHIR"])[:3]
    while len(steps) < 3:
        steps.append("")
    xs = [220, 600, 980]
    kinds = ["server", "node", "cloud"]
    colors = [(148, 163, 184), theme["accent"], (20, 184, 166)]
    for i, (x, label, kind, color) in enumerate(zip(xs, steps, kinds, colors)):
        _icon_circle(draw, (x, 500), color, kind)
        for j, line in enumerate(_wrap(str(label), fonts["label"], 280, draw)[:2]):
            tw = draw.textlength(line, font=fonts["label"])
            draw.text((x - tw / 2, 600 + j * 36), line, font=fonts["label"], fill=theme["ink"])
        if i < 2:
            draw.polygon([(x + 70, 490), (x + 110, 500), (x + 70, 510)], fill=colors[i + 1])

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

    header = theme.get("header", (30, 64, 175))
    draw.rectangle([0, 0, WIDTH, 220], fill=header)
    title = _title(post)
    y = 50
    for line in _wrap(title, fonts["title"], 1080, draw)[:2]:
        draw.text((50, y), line, font=fonts["title"], fill=(255, 255, 255))
        y += 58
    sub = _subtitle(post)
    if sub:
        draw.text((50, 160), sub[:90], font=fonts["small"], fill=(220, 230, 255))

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
        draw.rounded_rectangle(
            [50, y0, WIDTH - 50, y0 + card_h],
            radius=18,
            fill=(255, 255, 255),
            outline=theme.get("line", (220, 220, 220)),
            width=2,
        )
        draw.rounded_rectangle([50, y0, 70, y0 + card_h], radius=8, fill=colors[i % len(colors)])
        draw.text((95, y0 + 24), str(i + 1), font=fonts["label"], fill=colors[i % len(colors)])
        ty = y0 + 28
        for line in _wrap(str(bullet), fonts["body"], 980, draw)[:3]:
            draw.text((140, ty), line, font=fonts["body"], fill=(30, 40, 60))
            ty += 30


def _layout_workflow(img: Any, draw: Any, fonts: dict[str, Any], post: dict[str, Any], theme: dict[str, Any]) -> None:
    draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(248, 250, 252))
    header = theme.get("header", (88, 28, 135))
    draw.rectangle([0, 0, WIDTH, 200], fill=header)
    title = _title(post)
    y = 50
    for line in _wrap(title, fonts["title"], 1100, draw)[:2]:
        draw.text((40, y), line, font=fonts["title"], fill=(255, 255, 255))
        y += 55
    sub = _subtitle(post)
    if sub:
        draw.text((40, 150), sub[:90], font=fonts["small"], fill=(230, 220, 255))

    steps = list(post.get("steps") or ["Request", "API", "Validate", "Decide", "Respond"])[:5]
    n = max(len(steps), 1)
    gap = 24
    usable = WIDTH - 80
    card_w = (usable - gap * (n - 1)) // n
    y0 = 300
    for i, step in enumerate(steps):
        x0 = 40 + i * (card_w + gap)
        draw.rounded_rectangle(
            [x0, y0, x0 + card_w, y0 + 520],
            radius=16,
            fill=(255, 255, 255),
            outline=theme["line"],
            width=2,
        )
        _icon_circle(
            draw,
            (x0 + card_w // 2, y0 + 90),
            theme["accent"] if i % 2 == 0 else theme["accent2"],
            "check" if i == n - 1 else "node",
        )
        draw.text((x0 + 14, y0 + 160), f"STEP {i + 1}", font=fonts["small"], fill=theme["accent"])
        ty = y0 + 200
        for line in _wrap(str(step), fonts["body"], card_w - 28, draw)[:6]:
            draw.text((x0 + 14, ty), line, font=fonts["body"], fill=(30, 30, 50))
            ty += 30


def _layout_dark_tech(img: Any, draw: Any, fonts: dict[str, Any], post: dict[str, Any], theme: dict[str, Any]) -> None:
    theme = THEMES["dark_green"] if post.get("accent_theme") != "navy" else THEMES["navy"]
    draw.rectangle([0, 0, WIDTH, HEIGHT], fill=theme["bg"])
    for y in range(0, HEIGHT, 40):
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

    y0 = y + 50
    for i, b in enumerate(bullets):
        yy = y0 + i * 120
        if yy + 100 > HEIGHT - 40:
            break
        draw.rounded_rectangle([50, yy, 700, yy + 100], radius=14, outline=theme["accent"], width=2)
        draw.ellipse([70, yy + 32, 100, yy + 62], fill=theme["accent"])
        draw.text((78, yy + 35), str(i + 1), font=fonts["small"], fill=theme["bg"])
        ty = yy + 24
        for line in _wrap(str(b), fonts["body"], 560, draw)[:2]:
            draw.text((120, ty), line, font=fonts["body"], fill=theme["ink"])
            ty += 30

    cx, cy = 960, 700
    draw.ellipse([cx - 110, cy - 110, cx + 110, cy + 110], outline=theme["accent"], width=3)
    hub = str(post.get("hub_label") or ("PAS" if "pas" in _title(post).lower() else "FHIR"))[:8]
    tw = draw.textlength(hub, font=fonts["label"])
    draw.text((cx - tw / 2, cy - 16), hub, font=fonts["label"], fill=theme["accent"])
    for x, y in [(960, 480), (1120, 620), (1100, 860), (820, 860), (800, 620)]:
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
    p = dict(post)
    layout = _layout(p)
    p["image_layout"] = layout
    if not p.get("image_title"):
        p["image_title"] = _title(p)
    if not p.get("accent_theme"):
        themes = ["blue", "teal", "navy", "orange", "purple", "dark_green"]
        p["accent_theme"] = {
            "split_compare": "green_split",
            "dark_tech": "dark_green",
        }.get(layout, themes[_seed(p) % len(themes)])
    if layout == "split_compare":
        p.setdefault("left_label", "Before")
        p.setdefault("right_label", "After")
        p.setdefault("left_points", ["Fragile", "Costly", "Hard to scale"])
        p.setdefault("right_points", ["Reusable", "Faster", "Product-ready"])
    elif layout == "before_after":
        p.setdefault("steps", ["Before", "Standard", "After"])
    elif layout == "workflow":
        p.setdefault("steps", ["Start", "Exchange", "Validate", "Decide", "Deliver"])
    elif layout in ("key_points", "dark_tech"):
        p.setdefault("bullets", ["Insight one", "Insight two", "Insight three", "Insight four"])
    p.setdefault("badge_labels", _badges(p))
    return p


def create_post_image(post: dict[str, Any], out_path: Path) -> Path:
    from PIL import Image, ImageDraw

    post = _enrich_defaults(post)
    layout = post["image_layout"]
    theme = _theme(post)
    if layout == "split_compare":
        theme = THEMES["green_split"]

    img = Image.new("RGB", (WIDTH, HEIGHT), theme.get("bg", (255, 255, 255)))
    draw = ImageDraw.Draw(img)
    fonts = _fonts()
    LAYOUTS.get(layout, _layout_title_network)(img, draw, fonts, post, theme)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, format="PNG", optimize=True)
    print(f"[image] Infographic '{layout}' / theme='{post.get('accent_theme')}' saved: {out_path.name}")
    return out_path


def image_path_for_draft(draft_md: Path) -> Path:
    return draft_md.with_suffix(".png")
