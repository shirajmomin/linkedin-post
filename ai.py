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
    """Use the chat LLM to invent a unique photorealistic LinkedIn cover brief."""
    topic = post.get("topic") or "healthcare interoperability"
    title = post.get("image_title") or post.get("hook") or topic
    system = (
        "You design photorealistic LinkedIn cover photo briefs for healthcare technology leaders. "
        "Return ONLY JSON: {\"prompt\": \"...\", \"scene\": \"...\"}. "
        "The prompt must describe a REALISTIC photograph (not cartoon, not flat infographic, not neon cyberpunk, not pure black). "
        "Bright or soft natural lighting, modern hospital / clinic / enterprise office / cloud ops center. "
        "May include professionals collaborating, glass architecture, subtle holographic UI without readable text. "
        "Absolutely no readable text, logos, watermarks, or brand names in the scene. "
        "Vertical portrait composition for LinkedIn. Vary the scene every time."
    )
    user = json.dumps(
        {
            "topic": topic,
            "headline_context": title,
            "bullets": list(post.get("bullets") or [])[:4],
            "style_goal": "Looks like a premium corporate LinkedIn photo, not AI clipart",
        }
    )
    result = call_llm(system, user)
    if result and (result.get("prompt") or "").strip():
        return str(result["prompt"]).strip()
    return _fallback_photo_prompt(post)


def _fallback_photo_prompt(post: dict[str, Any]) -> str:
    import random

    topic = post.get("topic") or "FHIR healthcare interoperability"
    title = post.get("image_title") or post.get("hook") or topic
    scenes = [
        "two healthcare technology architects reviewing a laptop in a bright modern hospital admin office, soft window light, shallow depth of field",
        "clinician and IT lead collaborating at a clean white desk with a tablet, contemporary clinic interior, natural daylight",
        "wide shot of a sunlit glass healthcare innovation hub with professionals walking, airy architecture, optimistic mood",
        "close candid of a solution architect presenting on a large monitor in a bright conference room, corporate healthcare setting",
        "modern data center aisle with cool soft lighting and a professional walking with a laptop, realistic photography not neon",
        "nurse practitioner using a tablet in a bright hospital corridor with gentle bokeh, authentic documentary style",
        "enterprise cloud operations floor with large windows and soft blue accent lighting, people collaborating, photorealistic",
        "healthcare executive handshake in a bright lobby with glass and wood finishes, premium corporate photography",
    ]
    scene = random.choice(scenes)
    return (
        f"Photorealistic LinkedIn cover photo about {title}. Scene: {scene}. "
        f"Theme: {topic}. Subtle soft cyan light trails suggesting secure data connectivity in the background, "
        "no readable text, no logos, no watermarks, 85mm lens look, high detail skin and fabric, "
        "magazine-quality healthcare technology editorial photography, vertical portrait composition."
    )


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

    model = env("OPENAI_IMAGE_MODEL", "dall-e-3")
    size = env("OPENAI_IMAGE_SIZE", "1024x1792")
    quality = env("OPENAI_IMAGE_QUALITY", "hd")
    safe_prompt = (
        f"{prompt.strip()}\n\n"
        "Camera: photorealistic DSLR photo, natural color, sharp focus, realistic people and materials. "
        "Avoid: illustration, cartoon, flat vector infographic, neon cyberpunk, pure black background, "
        "readable text, letters, logos, watermarks, UI screens with words. "
        "Vertical LinkedIn portrait cover."
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
        elif quality:
            kwargs["quality"] = quality if quality in ("low", "medium", "high", "auto") else "high"

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
        f"photorealistic LinkedIn healthcare technology cover photo, {clean}, "
        "sharp focus, natural light, no text, no watermark, no logo, vertical"
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
    """Generate a photorealistic LinkedIn image via OpenAI (optional Pollinations)."""
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
