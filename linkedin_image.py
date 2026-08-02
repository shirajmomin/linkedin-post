"""Enterprise LinkedIn HealthTech infographics (1080x1350).

Light backgrounds only. Randomized layout + palette each run.
Never black / neon cyberpunk HUD. No author name on the image.
"""

from __future__ import annotations

import json
import secrets
from pathlib import Path
from typing import Any

WIDTH = 1080
HEIGHT = 1350

ROOT = Path(__file__).resolve().parent
CONCEPT_PATH = ROOT / ".last_image_concept.json"

# --- Background families (light only) ----------------------------------------
BACKGROUNDS = {
    "light_blue_gradient": ((230, 242, 255), (200, 220, 245)),
    "white_azure": ((255, 255, 255), (232, 244, 255)),
    "soft_teal_gradient": ((232, 250, 248), (200, 235, 230)),
    "light_gray_enterprise": ((245, 247, 250), (230, 234, 240)),
    "healthcare_cyan": ((225, 245, 250), (190, 230, 240)),
    "white_glass": ((252, 253, 255), (238, 242, 250)),
    "soft_purple_enterprise": ((245, 240, 255), (228, 220, 250)),
    "light_green_healthcare": ((240, 252, 245), (210, 240, 220)),
    "white_navy": ((255, 255, 255), (232, 238, 248)),
    "cloud_sky": ((236, 246, 255), (210, 228, 245)),
    "frosted_glass": ((248, 250, 252), (228, 236, 245)),
    "soft_orange_tech": ((255, 248, 240), (255, 232, 210)),
}

# --- Color palettes ----------------------------------------------------------
PALETTES = {
    "A": {  # White, Azure, Teal
        "ink": (20, 45, 80),
        "muted": (90, 110, 135),
        "accent": (0, 120, 212),
        "accent2": (0, 160, 170),
        "card": (255, 255, 255),
        "line": (190, 210, 230),
    },
    "B": {  # Light Gray, Navy, Cyan
        "ink": (15, 30, 60),
        "muted": (100, 115, 135),
        "accent": (10, 40, 90),
        "accent2": (0, 180, 200),
        "card": (255, 255, 255),
        "line": (200, 208, 220),
    },
    "C": {  # Soft Purple, White, Indigo
        "ink": (40, 30, 80),
        "muted": (110, 100, 140),
        "accent": (90, 70, 180),
        "accent2": (120, 100, 200),
        "card": (255, 255, 255),
        "line": (210, 200, 230),
    },
    "D": {  # Light Green, Emerald, White
        "ink": (20, 60, 45),
        "muted": (90, 120, 105),
        "accent": (16, 150, 110),
        "accent2": (40, 180, 130),
        "card": (255, 255, 255),
        "line": (190, 220, 200),
    },
    "E": {  # Sky Blue, White, Dark Blue
        "ink": (10, 35, 80),
        "muted": (100, 120, 150),
        "accent": (50, 140, 220),
        "accent2": (20, 60, 130),
        "card": (255, 255, 255),
        "line": (200, 220, 240),
    },
    "F": {  # Orange Accent, White, Slate
        "ink": (40, 45, 55),
        "muted": (110, 115, 125),
        "accent": (230, 126, 34),
        "accent2": (70, 80, 95),
        "card": (255, 255, 255),
        "line": (210, 215, 220),
    },
}

LAYOUTS_META = [
    "executive_dashboard",
    "workflow_diagram",
    "timeline_roadmap",
    "architecture_blueprint",
    "data_visualization",
    "feature_comparison",
    "compliance_checklist",
    "kpi_metrics",
    "api_ecosystem",
    "process_flow",
    "healthcare_network",
    "modern_card",
    "infographic_wheel",
    "split_screen",
    "hero_statistic",
]

# Topic → preferred layout families (still randomized within + uniqueness)
TOPIC_LAYOUT_HINTS = {
    "0057": ["compliance_checklist", "timeline_roadmap", "workflow_diagram", "api_ecosystem", "executive_dashboard"],
    "prior": ["workflow_diagram", "process_flow", "compliance_checklist", "timeline_roadmap"],
    "crd": ["workflow_diagram", "process_flow", "api_ecosystem"],
    "fhir": ["architecture_blueprint", "api_ecosystem", "healthcare_network", "modern_card"],
    "azure": ["architecture_blueprint", "executive_dashboard", "api_ecosystem", "kpi_metrics"],
    "dotnet": ["architecture_blueprint", "executive_dashboard", "modern_card", "hero_statistic"],
    ".net": ["architecture_blueprint", "executive_dashboard", "modern_card"],
    "security": ["compliance_checklist", "feature_comparison", "modern_card"],
    "oauth": ["feature_comparison", "architecture_blueprint", "compliance_checklist"],
    "patient": ["healthcare_network", "hero_statistic", "modern_card", "kpi_metrics"],
    "directory": ["data_visualization", "feature_comparison", "api_ecosystem"],
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
        "display": ImageFont.truetype(bold, 52 * s),
        "hero": ImageFont.truetype(bold, 44 * s),
        "h1": ImageFont.truetype(bold, 36 * s),
        "h2": ImageFont.truetype(bold, 28 * s),
        "h3": ImageFont.truetype(bold, 22 * s),
        "body": ImageFont.truetype(reg, 20 * s),
        "small": ImageFont.truetype(reg, 17 * s),
        "tiny": ImageFont.truetype(reg, 14 * s),
    }


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


def _short_headline(post: dict[str, Any], max_words: int = 8) -> str:
    raw = (post.get("image_title") or post.get("hook") or post.get("topic") or "FHIR Interoperability").strip()
    words = raw.split()
    return " ".join(words[:max_words])


def _short_support(post: dict[str, Any], max_words: int = 6) -> str:
    raw = (post.get("highlight") or post.get("image_subtitle") or post.get("cta") or "").strip()
    if not raw:
        return ""
    return " ".join(raw.split()[:max_words])


def _cards(post: dict[str, Any], n: int = 4) -> list[str]:
    items = list(post.get("bullets") or post.get("steps") or post.get("badge_labels") or [])
    if not items:
        items = ["FHIR APIs", "CMS Interop", "Prior Auth", "Cloud Scale"]
    out = []
    for x in items[:n]:
        out.append(" ".join(str(x).split()[:4]))
    while len(out) < n:
        out.append(["FHIR", "API", "Cloud", "Trust"][len(out) % 4])
    return out


def _load_last_concept() -> dict[str, Any]:
    if not CONCEPT_PATH.exists():
        return {}
    try:
        return json.loads(CONCEPT_PATH.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}


def _save_concept(concept: dict[str, Any]) -> None:
    CONCEPT_PATH.write_text(json.dumps(concept, indent=2), encoding="utf-8")


def _hint_layouts(post: dict[str, Any]) -> list[str]:
    t = f"{post.get('topic', '')} {post.get('image_title', '')}".lower()
    for needle, layouts in TOPIC_LAYOUT_HINTS.items():
        if needle in t:
            return layouts
    return list(LAYOUTS_META)


def pick_unique_concept(post: dict[str, Any]) -> dict[str, Any]:
    """Pick layout + palette + background different from the previous run."""
    last = _load_last_concept()
    hints = _hint_layouts(post)
    pool = list(dict.fromkeys(hints + LAYOUTS_META))  # hints first, then all

    for _ in range(24):
        layout = secrets.choice(pool)
        background = secrets.choice(list(BACKGROUNDS.keys()))
        palette = secrets.choice(list(PALETTES.keys()))
        # Uniqueness: change layout AND (palette or background) vs last
        if last:
            same_layout = layout == last.get("layout")
            same_look = background == last.get("background_theme") and palette == last.get("color_palette")
            if same_layout or same_look:
                continue
        concept = {
            "image_style": "enterprise_healthcare_saas",
            "background_theme": background,
            "layout": layout,
            "color_palette": palette,
            "headline": _short_headline(post),
            "visual_elements": _cards(post, 4),
            "design_description": f"{layout} on {background} with palette {palette}",
            "linkedin_optimized": True,
        }
        return concept

    # Fallback: force different layout from last
    layout = secrets.choice([L for L in LAYOUTS_META if L != last.get("layout")] or LAYOUTS_META)
    background = secrets.choice([b for b in BACKGROUNDS if b != last.get("background_theme")] or list(BACKGROUNDS))
    palette = secrets.choice([p for p in PALETTES if p != last.get("color_palette")] or list(PALETTES))
    return {
        "image_style": "enterprise_healthcare_saas",
        "background_theme": background,
        "layout": layout,
        "color_palette": palette,
        "headline": _short_headline(post),
        "visual_elements": _cards(post, 4),
        "design_description": f"{layout} on {background} with palette {palette}",
        "linkedin_optimized": True,
    }


def _canvas(bg_key: str) -> Any:
    from PIL import Image, ImageDraw

    c1, c2 = BACKGROUNDS[bg_key]
    img = Image.new("RGB", (WIDTH, HEIGHT), c1)
    d = ImageDraw.Draw(img)
    for y in range(HEIGHT):
        t = y / max(HEIGHT - 1, 1)
        r = int(c1[0] + (c2[0] - c1[0]) * t)
        g = int(c1[1] + (c2[1] - c1[1]) * t)
        b = int(c1[2] + (c2[2] - c1[2]) * t)
        d.line([(0, y), (WIDTH, y)], fill=(r, g, b))
    return img


def _card(d: Any, box: tuple[int, int, int, int], pal: dict, radius: int = 18) -> None:
    d.rounded_rectangle(list(box), radius=radius, fill=pal["card"], outline=pal["line"], width=2)


def _icon_dot(d: Any, xy: tuple[int, int], color: tuple[int, int, int], r: int = 18) -> None:
    x, y = xy
    d.ellipse([x - r, y - r, x + r, y + r], fill=color)


# --- Layouts -----------------------------------------------------------------


def _lay_executive_dashboard(img: Any, post: dict, fonts: dict, pal: dict, concept: dict) -> Any:
    from PIL import ImageDraw

    d = ImageDraw.Draw(img)
    headline = concept["headline"]
    d.text((48, 48), "EXECUTIVE VIEW", font=fonts["tiny"], fill=pal["accent"])
    y = 90
    for line in _wrap(headline, fonts["hero"], WIDTH - 100, d)[:2]:
        d.text((48, y), line, font=fonts["hero"], fill=pal["ink"])
        y += 54

    metrics = _cards(post, 4)
    labels = ["Ready", "In Flight", "Risk", "Done"]
    positions = [(48, 280), (560, 280), (48, 620), (560, 620)]
    for (x, y), m, lab in zip(positions, metrics, labels):
        _card(d, (x, y, x + 470, y + 280), pal, 22)
        d.text((x + 36, y + 40), lab, font=fonts["small"], fill=pal["muted"])
        d.text((x + 36, y + 100), m[:18], font=fonts["h2"], fill=pal["accent"])
        d.rectangle([x + 36, y + 200, x + 200, y + 220], fill=pal["accent2"])
    return img


def _lay_workflow_diagram(img: Any, post: dict, fonts: dict, pal: dict, concept: dict) -> Any:
    from PIL import ImageDraw

    d = ImageDraw.Draw(img)
    d.text((48, 50), concept["headline"][:42], font=fonts["h1"], fill=pal["ink"])
    steps = _cards(post, 4)
    y = 200
    for i, step in enumerate(steps):
        _card(d, (100, y, WIDTH - 100, y + 140), pal, 20)
        _icon_dot(d, (170, y + 70), pal["accent"], 28)
        d.text((155, y + 55), str(i + 1), font=fonts["h3"], fill=(255, 255, 255))
        d.text((230, y + 50), step[:28], font=fonts["h2"], fill=pal["ink"])
        if i < len(steps) - 1:
            d.line([(170, y + 140), (170, y + 180)], fill=pal["accent2"], width=4)
        y += 200
    return img


def _lay_timeline_roadmap(img: Any, post: dict, fonts: dict, pal: dict, concept: dict) -> Any:
    from PIL import ImageDraw

    d = ImageDraw.Draw(img)
    d.text((48, 50), concept["headline"][:40], font=fonts["h1"], fill=pal["ink"])
    d.line([(120, 280), (120, HEIGHT - 160)], fill=pal["accent"], width=6)
    steps = _cards(post, 4)
    y = 260
    for i, step in enumerate(steps):
        _icon_dot(d, (120, y + 40), pal["accent2"], 22)
        _card(d, (200, y, WIDTH - 60, y + 120), pal, 16)
        d.text((230, y + 40), step[:30], font=fonts["h3"], fill=pal["ink"])
        y += 200
    return img


def _lay_architecture_blueprint(img: Any, post: dict, fonts: dict, pal: dict, concept: dict) -> Any:
    from PIL import ImageDraw

    d = ImageDraw.Draw(img)
    d.text((48, 40), concept["headline"][:38], font=fonts["h1"], fill=pal["ink"])
    layers = _cards(post, 4)
    colors = [pal["accent"], pal["accent2"], pal["ink"], pal["muted"]]
    y = 180
    for i, layer in enumerate(layers):
        d.rounded_rectangle([80, y, WIDTH - 80, y + 150], radius=18, fill=colors[i % 4])
        d.text((120, y + 55), layer[:32], font=fonts["h2"], fill=(255, 255, 255))
        if i < len(layers) - 1:
            d.polygon([(WIDTH // 2 - 14, y + 158), (WIDTH // 2 + 14, y + 158), (WIDTH // 2, y + 180)], fill=pal["ink"])
        y += 200
    return img


def _lay_data_visualization(img: Any, post: dict, fonts: dict, pal: dict, concept: dict) -> Any:
    from PIL import ImageDraw

    d = ImageDraw.Draw(img)
    d.text((48, 48), concept["headline"][:40], font=fonts["h1"], fill=pal["ink"])
    _card(d, (60, 200, WIDTH - 60, 900), pal, 24)
    # faux bars
    heights = [180, 280, 220, 340, 260, 300]
    base = 820
    for i, h in enumerate(heights):
        x = 120 + i * 140
        d.rounded_rectangle([x, base - h, x + 80, base], radius=10, fill=pal["accent"] if i % 2 == 0 else pal["accent2"])
    support = _short_support(post) or "Interop readiness"
    d.text((80, 960), support[:36], font=fonts["h3"], fill=pal["muted"])
    return img


def _lay_feature_comparison(img: Any, post: dict, fonts: dict, pal: dict, concept: dict) -> Any:
    from PIL import ImageDraw

    d = ImageDraw.Draw(img)
    mid = WIDTH // 2
    d.rectangle([0, 0, mid, HEIGHT], fill=tuple(min(255, c + 8) for c in BACKGROUNDS.get("light_gray_enterprise", ((240, 240, 240),))[0]))
    # keep canvas; draw panels
    _card(d, (40, 160, mid - 30, HEIGHT - 80), pal, 22)
    _card(d, (mid + 30, 160, WIDTH - 40, HEIGHT - 80), pal, 22)
    left = (post.get("left_label") or "Legacy")[:22]
    right = (post.get("right_label") or "FHIR")[:22]
    d.text((70, 200), left, font=fonts["h2"], fill=pal["muted"])
    d.text((mid + 60, 200), right, font=fonts["h2"], fill=pal["accent"])
    d.text((48, 50), concept["headline"][:36], font=fonts["h1"], fill=pal["ink"])
    left_pts = list(post.get("left_points") or _cards(post, 3))[:3]
    right_pts = list(post.get("right_points") or _cards(post, 3))[:3]
    y = 300
    for a, b in zip(left_pts, right_pts):
        d.text((70, y), str(a)[:24], font=fonts["body"], fill=pal["ink"])
        d.text((mid + 60, y), str(b)[:24], font=fonts["body"], fill=pal["ink"])
        y += 80
    return img


def _lay_compliance_checklist(img: Any, post: dict, fonts: dict, pal: dict, concept: dict) -> Any:
    from PIL import ImageDraw

    d = ImageDraw.Draw(img)
    d.text((48, 48), concept["headline"][:40], font=fonts["h1"], fill=pal["ink"])
    items = _cards(post, 5)
    y = 200
    for item in items:
        _card(d, (60, y, WIDTH - 60, y + 130), pal, 18)
        d.rounded_rectangle([90, y + 40, 150, y + 95], radius=10, fill=pal["accent2"])
        d.text((105, y + 52), "✓", font=fonts["h2"], fill=(255, 255, 255))
        d.text((180, y + 48), item[:28], font=fonts["h3"], fill=pal["ink"])
        y += 160
    return img


def _lay_kpi_metrics(img: Any, post: dict, fonts: dict, pal: dict, concept: dict) -> Any:
    from PIL import ImageDraw

    d = ImageDraw.Draw(img)
    d.text((48, 48), concept["headline"][:38], font=fonts["h1"], fill=pal["ink"])
    kpis = [("98%", "API Uptime"), ("3×", "Faster PA"), ("40%", "Less Fax"), ("24/7", "Access")]
    # blend with post cards as labels when present
    cards = _cards(post, 4)
    positions = [(48, 220), (560, 220), (48, 700), (560, 700)]
    for (x, y), (val, lab), card in zip(positions, kpis, cards):
        _card(d, (x, y, x + 470, y + 380), pal, 24)
        d.text((x + 40, y + 80), val, font=fonts["display"], fill=pal["accent"])
        d.text((x + 40, y + 200), (card or lab)[:18], font=fonts["h3"], fill=pal["ink"])
    return img


def _lay_api_ecosystem(img: Any, post: dict, fonts: dict, pal: dict, concept: dict) -> Any:
    from PIL import ImageDraw

    d = ImageDraw.Draw(img)
    d.text((48, 40), concept["headline"][:36], font=fonts["h1"], fill=pal["ink"])
    cx, cy = WIDTH // 2, HEIGHT // 2 + 40
    _icon_dot(d, (cx, cy), pal["accent"], 70)
    d.text((cx - 36, cy - 16), "FHIR", font=fonts["h3"], fill=(255, 255, 255))
    nodes = _cards(post, 6)
    coords = [
        (200, 280),
        (880, 280),
        (160, 700),
        (920, 700),
        (300, 1050),
        (780, 1050),
    ]
    for (x, y), label in zip(coords, nodes):
        d.line([(cx, cy), (x, y)], fill=pal["line"], width=3)
        _card(d, (x - 110, y - 50, x + 110, y + 50), pal, 16)
        tw = d.textlength(label[:14], font=fonts["small"])
        d.text((x - tw / 2, y - 12), label[:14], font=fonts["small"], fill=pal["ink"])
    return img


def _lay_process_flow(img: Any, post: dict, fonts: dict, pal: dict, concept: dict) -> Any:
    from PIL import ImageDraw

    d = ImageDraw.Draw(img)
    d.text((48, 50), concept["headline"][:40], font=fonts["h1"], fill=pal["ink"])
    steps = _cards(post, 3)
    xs = [120, 420, 720]
    y = 420
    for i, (x, step) in enumerate(zip(xs, steps)):
        _card(d, (x, y, x + 240, y + 280), pal, 20)
        _icon_dot(d, (x + 120, y + 80), pal["accent"], 36)
        for j, line in enumerate(_wrap(step, fonts["body"], 200, d)[:3]):
            tw = d.textlength(line, font=fonts["body"])
            d.text((x + 120 - tw / 2, y + 150 + j * 28), line, font=fonts["body"], fill=pal["ink"])
        if i < 2:
            d.polygon([(x + 250, y + 140), (x + 290, y + 160), (x + 250, y + 180)], fill=pal["accent2"])
    return img


def _lay_healthcare_network(img: Any, post: dict, fonts: dict, pal: dict, concept: dict) -> Any:
    from PIL import ImageDraw

    d = ImageDraw.Draw(img)
    d.text((48, 48), concept["headline"][:38], font=fonts["h1"], fill=pal["ink"])
    # network grid of nodes
    nodes = [(200, 350), (540, 280), (880, 350), (300, 700), (700, 700), (540, 1000)]
    for i, (x1, y1) in enumerate(nodes):
        for x2, y2 in nodes[i + 1 :]:
            d.line([(x1, y1), (x2, y2)], fill=pal["line"], width=2)
    labels = _cards(post, 6)
    for (x, y), lab in zip(nodes, labels):
        _icon_dot(d, (x, y), pal["accent"], 26)
        tw = d.textlength(lab[:12], font=fonts["tiny"])
        d.text((x - tw / 2, y + 40), lab[:12], font=fonts["tiny"], fill=pal["ink"])
    return img


def _lay_modern_card(img: Any, post: dict, fonts: dict, pal: dict, concept: dict) -> Any:
    from PIL import ImageDraw

    d = ImageDraw.Draw(img)
    _card(d, (60, 120, WIDTH - 60, HEIGHT - 120), pal, 28)
    d.rectangle([60, 120, 90, HEIGHT - 120], fill=pal["accent"])
    y = 200
    for line in _wrap(concept["headline"], fonts["hero"], WIDTH - 200, d)[:3]:
        d.text((130, y), line, font=fonts["hero"], fill=pal["ink"])
        y += 58
    support = _short_support(post)
    if support:
        d.text((130, y + 20), support[:40], font=fonts["h3"], fill=pal["accent2"])
    chips = _cards(post, 3)
    bx = 130
    by = HEIGHT - 280
    for c in chips:
        tw = int(d.textlength(c[:14], font=fonts["small"]))
        d.rounded_rectangle([bx, by, bx + tw + 40, by + 50], radius=14, fill=pal["accent"])
        d.text((bx + 20, by + 14), c[:14], font=fonts["small"], fill=(255, 255, 255))
        bx += tw + 56
    return img


def _lay_infographic_wheel(img: Any, post: dict, fonts: dict, pal: dict, concept: dict) -> Any:
    from PIL import ImageDraw
    import math

    d = ImageDraw.Draw(img)
    d.text((48, 40), concept["headline"][:36], font=fonts["h1"], fill=pal["ink"])
    cx, cy, R = WIDTH // 2, HEIGHT // 2 + 40, 280
    d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=pal["accent"], width=8)
    d.ellipse([cx - 90, cy - 90, cx + 90, cy + 90], fill=pal["accent2"])
    d.text((cx - 40, cy - 14), "FHIR", font=fonts["h3"], fill=(255, 255, 255))
    items = _cards(post, 6)
    for i, lab in enumerate(items):
        ang = -math.pi / 2 + i * (2 * math.pi / len(items))
        x = cx + int((R + 90) * math.cos(ang))
        y = cy + int((R + 90) * math.sin(ang))
        tw = d.textlength(lab[:12], font=fonts["small"])
        d.text((x - tw / 2, y - 10), lab[:12], font=fonts["small"], fill=pal["ink"])
    return img


def _lay_split_screen(img: Any, post: dict, fonts: dict, pal: dict, concept: dict) -> Any:
    from PIL import ImageDraw

    d = ImageDraw.Draw(img)
    mid = WIDTH // 2
    d.rectangle([0, 0, mid, HEIGHT], fill=pal["line"])
    d.rectangle([mid, 0, WIDTH, HEIGHT], fill=pal["card"])
    left = (post.get("left_label") or "Before")[:20]
    right = (post.get("right_label") or "With FHIR")[:20]
    for i, line in enumerate(_wrap(left, fonts["h1"], mid - 80, d)[:3]):
        d.text((40, 400 + i * 50), line, font=fonts["h1"], fill=pal["ink"])
    for i, line in enumerate(_wrap(right, fonts["h1"], mid - 80, d)[:3]):
        d.text((mid + 40, 400 + i * 50), line, font=fonts["h1"], fill=pal["accent"])
    d.text((40, 60), concept["headline"][:30], font=fonts["h3"], fill=pal["muted"])
    return img


def _lay_hero_statistic(img: Any, post: dict, fonts: dict, pal: dict, concept: dict) -> Any:
    from PIL import ImageDraw

    d = ImageDraw.Draw(img)
    stat = (post.get("highlight") or "2027").strip().split()[0][:8]
    if len(stat) > 6:
        stat = "3×"
    tw = d.textlength(stat, font=fonts["display"])
    # oversized feel using repeated h1 if needed
    d.text(((WIDTH - tw) / 2, 280), stat, font=fonts["display"], fill=pal["accent"])
    y = 420
    for line in _wrap(concept["headline"], fonts["h1"], WIDTH - 120, d)[:3]:
        tw2 = d.textlength(line, font=fonts["h1"])
        d.text(((WIDTH - tw2) / 2, y), line, font=fonts["h1"], fill=pal["ink"])
        y += 50
    support = _short_support(post)
    if support:
        tw3 = d.textlength(support[:40], font=fonts["body"])
        d.text(((WIDTH - tw3) / 2, y + 40), support[:40], font=fonts["body"], fill=pal["muted"])
    return img


LAYOUT_RENDERERS = {
    "executive_dashboard": _lay_executive_dashboard,
    "workflow_diagram": _lay_workflow_diagram,
    "timeline_roadmap": _lay_timeline_roadmap,
    "architecture_blueprint": _lay_architecture_blueprint,
    "data_visualization": _lay_data_visualization,
    "feature_comparison": _lay_feature_comparison,
    "compliance_checklist": _lay_compliance_checklist,
    "kpi_metrics": _lay_kpi_metrics,
    "api_ecosystem": _lay_api_ecosystem,
    "process_flow": _lay_process_flow,
    "healthcare_network": _lay_healthcare_network,
    "modern_card": _lay_modern_card,
    "infographic_wheel": _lay_infographic_wheel,
    "split_screen": _lay_split_screen,
    "hero_statistic": _lay_hero_statistic,
}


def create_post_image(post: dict[str, Any], out_path: Path) -> Path:
    """Render a unique light enterprise LinkedIn image every run."""
    global WIDTH, HEIGHT
    WIDTH, HEIGHT = 1080, 1350

    concept = pick_unique_concept(post)
    fonts = _fonts(1)
    pal = PALETTES[concept["color_palette"]]
    img = _canvas(concept["background_theme"])
    renderer = LAYOUT_RENDERERS[concept["layout"]]
    img = renderer(img, post, fonts, pal, concept)

    if img.mode != "RGB":
        img = img.convert("RGB")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, format="PNG", compress_level=4)
    _save_concept(concept)

    print(
        f"[image] layout={concept['layout']} bg={concept['background_theme']} "
        f"palette={concept['color_palette']} -> {out_path.name}"
    )
    # Attach concept for callers/tests
    post["_image_concept"] = concept
    return out_path
