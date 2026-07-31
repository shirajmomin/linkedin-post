"""Shared paths, config, and profile loading for the LinkedIn agent."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

DATA_DIR = ROOT / "data"
DRAFTS_DIR = ROOT / "drafts"
PROMPTS_DIR = ROOT / "prompts"


def load_profile() -> dict[str, Any]:
    with open(ROOT / "profile.json", encoding="utf-8") as f:
        return json.load(f)


def load_config() -> dict[str, Any]:
    with open(ROOT / "config.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_prompt(name: str) -> str:
    return (PROMPTS_DIR / name).read_text(encoding="utf-8")


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DRAFTS_DIR.mkdir(parents=True, exist_ok=True)


def env(key: str, default: str = "") -> str:
    return os.getenv(key, default).strip()
