"""Shared paths, config, cleanup, and profile loading for the LinkedIn agent."""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

ASSETS_DIR = ROOT / "assets"
PROMPTS_DIR = ROOT / "prompts"

# Legacy folders — deleted on every run; never used for storage
_LEGACY_DIRS = (ROOT / "drafts", ROOT / "data")


def load_profile() -> dict[str, Any]:
    with open(ROOT / "profile.json", encoding="utf-8") as f:
        return json.load(f)


def load_config() -> dict[str, Any]:
    with open(ROOT / "config.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_prompt(name: str) -> str:
    return (PROMPTS_DIR / name).read_text(encoding="utf-8")


def env(key: str, default: str = "") -> str:
    return os.getenv(key, default).strip()


def cleanup_runtime_files(extra_dirs: list[Path] | None = None) -> None:
    """Remove temp dirs and any leftover drafts/data/assets — nothing is persisted."""
    for legacy in _LEGACY_DIRS:
        if legacy.exists():
            shutil.rmtree(legacy, ignore_errors=True)

    if ASSETS_DIR.exists():
        for p in ASSETS_DIR.glob("*.png"):
            p.unlink(missing_ok=True)

    pyc = ROOT / "__pycache__"
    if pyc.exists():
        shutil.rmtree(pyc, ignore_errors=True)

    for d in extra_dirs or []:
        if d and Path(d).exists():
            shutil.rmtree(d, ignore_errors=True)
