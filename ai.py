"""LLM + image helpers for LinkedIn post generation (OpenAI / Anthropic)."""

from __future__ import annotations

import base64
import json
import re
import urllib.parse
import urllib.request
from typing import Any

from common import env


def call_openai(system: str, user: str) -> dict[str, Any] | None:
    api_key = env("OPENAI_API_KEY")
    if not api_key:
        return None
    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        model = env("OPENAI_MODEL", "gpt-4o-mini")
        resp = client.chat.completions.create(
            model=model,
            temperature=0.85,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            response_format={"type": "json_object"},
        )
        return json.loads(resp.choices[0].message.content or "{}")
    except Exception as exc:  # noqa: BLE001
        print(f"[openai] {exc}")
        return None


def call_anthropic(system: str, user: str) -> dict[str, Any] | None:
    api_key = env("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    try:
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)
        model = env("ANTHROPIC_MODEL", "claude-sonnet-4-6")
        resp = client.messages.create(
            model=model,
            max_tokens=1400,
            temperature=0.85,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        text = resp.content[0].text if resp.content else "{}"
        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\n?", "", text)
            text = re.sub(r"\n?```$", "", text)
        return json.loads(text)
    except Exception as exc:  # noqa: BLE001
        print(f"[anthropic] {exc}")
        return None


def call_llm(system: str, user: str) -> dict[str, Any] | None:
    provider = env("AI_PROVIDER", "openai").lower()
    if provider == "anthropic":
        result = call_anthropic(system, user)
        if result:
            return result
    result = call_openai(system, user)
    if result:
        return result
    if provider != "anthropic":
        return call_anthropic(system, user)
    return None


def draft_image_prompt(post: dict[str, Any]) -> str:
    """LLM writes a premium USA healthcare LinkedIn INFGRAPHIC prompt (text+cards)."""
    from common import load_prompt

    topic = post.get("topic") or "USA healthcare interoperability"
    title = post.get("image_title") or post.get("hook") or topic
    alert = (post.get("alert_label") or "HEALTH IT").strip()
    bullets = list(post.get("bullets") or [])[:4]
    while len(bullets) < 4:
        bullets.append(
            [
                "Coverage rules at order time",
                "Avoid denial after care",
                "Faster clinician decisions",
                "Standards-based FHIR exchange",
            ][len(bullets)]
        )
    badges = list(post.get("badge_labels") or ["CMS-0057-F", "Da Vinci", "FHIR"])[:4]
    footer = post.get("footer_note") or " · ".join(badges)
    highlight = post.get("highlight") or post.get("image_subtitle") or ""

    try:
        system = load_prompt("linkedin_image_prompt.txt")
    except Exception:  # noqa: BLE001
        system = (
            "Design a premium light-enterprise USA healthcare LinkedIn infographic prompt. "
            "Return JSON with key prompt. Include exact headline and 4 card texts."
        )

    user = json.dumps(
        {
            "topic": topic,
            "alert_badge_text": alert[:24],
            "headline_text": " ".join(str(title).split()[:10]),
            "support_text": " ".join(str(highlight).split()[:12]),
            "card_01": " ".join(str(bullets[0]).split()[:8]),
            "card_02": " ".join(str(bullets[1]).split()[:8]),
            "card_03": " ".join(str(bullets[2]).split()[:8]),
            "card_04": " ".join(str(bullets[3]).split()[:8]),
            "footer_text": str(footer)[:70],
            "must_include_exact_text": True,
            "reference_style": (
                "Like a senior health-tech designer: soft blue gradient, navy headline, "
                "teal accents, white rounded cards with icons and 01-04 numbers, footer pill, "
                "no black neon cyberpunk, LinkedIn-ready."
            ),
        },
        indent=2,
    )
    result = call_llm(system, user)
    if result and (result.get("prompt") or "").strip():
        return str(result["prompt"]).strip()
    return _fallback_infographic_prompt(post)


def _fallback_infographic_prompt(post: dict[str, Any]) -> str:
    title = " ".join(
        (
            post.get("image_title")
            or post.get("hook")
            or "Why check Prior Auth first"
        ).split()[:10]
    )
    alert = (post.get("alert_label") or "CRD")[:20]
    bullets = list(post.get("bullets") or [])[:4]
    defaults = [
        "Does this order need auth",
        "Coverage rules at order time",
        "Avoid denial after care",
        "Faster clinician decisions",
    ]
    while len(bullets) < 4:
        bullets.append(defaults[len(bullets)])
    cards = [" ".join(str(b).split()[:8]) for b in bullets]
    footer = post.get("footer_note") or "CMS-0057-F · Da Vinci · FHIR"
    return (
        f"Premium LinkedIn healthcare technology infographic, vertical portrait, "
        f"soft light-blue gradient background with subtle wavy lines and faint dot grid, "
        f"enterprise SaaS clinical design, navy and teal accents, white cards with soft shadows. "
        f"Top center dark-blue rounded badge with white text '{alert}'. "
        f"Large bold navy headline '{title}'. "
        f"Four white rounded cards in a 2x2 grid labeled 01 to 04 with simple teal/navy line icons: "
        f"01 '{cards[0]}', 02 '{cards[1]}', 03 '{cards[2]}', 04 '{cards[3]}'. "
        f"Bottom white pill footer with text '{footer}'. "
        f"Clean modern sans-serif typography, high readability, generous whitespace, "
        f"no photorealistic people, no vendor logos, no watermarks, no black cyberpunk neon."
    )


def _fallback_photo_prompt(post: dict[str, Any]) -> str:
    # Kept for compatibility; prefer infographic path
    return _fallback_infographic_prompt(post)


def _download(url: str, timeout: int = 120) -> bytes | None:
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "LinkedInPostAgent/1.0"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except Exception as exc:  # noqa: BLE001
        print(f"[image] Download failed: {exc}")
        return None


def _openai_image(prompt: str) -> bytes | None:
    api_key = env("OPENAI_API_KEY")
    if not api_key:
        return None

    # gpt-image-1 is stronger for text-on-image infographics than dall-e-3
    model = env("OPENAI_IMAGE_MODEL", "gpt-image-1")
    size = env("OPENAI_IMAGE_SIZE", "1024x1536")
    quality = env("OPENAI_IMAGE_QUALITY", "high")
    safe_prompt = (
        f"{prompt.strip()}\n\n"
        "Render as a finished LinkedIn infographic with crisp readable text exactly as specified. "
        "Light enterprise healthcare design: soft blue/white background, navy + teal accents, "
        "white cards, clean sans-serif type. No black neon cyberpunk. No watermarks. No vendor logos."
    )

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        print(f"[image] OpenAI image model={model} size={size} quality={quality}")
        kwargs: dict[str, Any] = {
            "model": model,
            "prompt": safe_prompt[:3900],
            "size": size,
            "n": 1,
        }
        if model.startswith("dall-e"):
            kwargs["quality"] = quality if quality in ("standard", "hd") else "hd"
            if size not in ("1024x1024", "1024x1792", "1792x1024"):
                kwargs["size"] = "1024x1792"
        else:
            # gpt-image-* 
            kwargs["quality"] = quality if quality in ("low", "medium", "high", "auto") else "high"
            if size not in ("1024x1024", "1024x1536", "1536x1024"):
                kwargs["size"] = "1024x1536"

        resp = client.images.generate(**kwargs)
        item = resp.data[0] if resp.data else None
        if not item:
            return None
        if getattr(item, "b64_json", None):
            return base64.b64decode(item.b64_json)
        if getattr(item, "url", None):
            return _download(item.url)
        return None
    except Exception as exc:  # noqa: BLE001
        print(f"[image] OpenAI image failed: {exc}")
        return None


def _pollinations_image(prompt: str) -> bytes | None:
    """Optional free Flux fallback (enable with IMAGE_POLLINATIONS=1)."""
    if env("IMAGE_POLLINATIONS", "0") not in ("1", "true", "yes"):
        return None
    clean = re.sub(r"\s+", " ", prompt.strip())[:400]
    clean = (
        f"premium LinkedIn healthcare infographic, light blue enterprise design, {clean}, "
        "crisp readable text, white cards, navy teal accents, no watermark, vertical"
    )
    encoded = urllib.parse.quote(clean)
    seed = abs(hash(clean)) % 99999
    url = (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width=1080&height=1350&seed={seed}&nologo=true&model=flux"
    )
    print("[image] Trying Pollinations Flux…")
    return _download(url, timeout=180)


def generate_ai_image(prompt: str) -> bytes | None:
    """Generate a premium LinkedIn healthcare infographic via OpenAI (optional Pollinations)."""
    provider = env("IMAGE_PROVIDER", "openai").lower()
    if provider in ("", "none", "local", "stock", "pillow"):
        return None

    if provider in ("openai", "auto"):
        raw = _openai_image(prompt)
        if raw:
            return raw
        print("[image] OpenAI unavailable — trying optional fallbacks")
        return _pollinations_image(prompt)

    if provider == "pollinations":
        return _pollinations_image(prompt)

    return None
