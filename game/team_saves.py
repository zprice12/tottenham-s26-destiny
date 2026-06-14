"""Named squad save files — create, list, load, delete."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SAVES_DIR = ROOT / "data" / "saves"


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def slugify(name: str) -> str:
    slug = name.strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug or "squad"


def _save_path(slug: str) -> Path:
    return SAVES_DIR / f"{slug}.json"


def ensure_saves_dir() -> None:
    SAVES_DIR.mkdir(parents=True, exist_ok=True)


def list_saves() -> list[dict]:
    ensure_saves_dir()
    saves = []
    for path in sorted(SAVES_DIR.glob("*.json")):
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            saves.append(
                {
                    "slug": data.get("slug", path.stem),
                    "name": data.get("name", path.stem),
                    "completed": data.get("completed", False),
                    "budget_m": data.get("budget_m", 0),
                    "squad_count": sum(
                        1
                        for p in data.get("players", [])
                        if p.get("status") in (
                            "depth_chart", "injured", "loan_return", "academy", "squad"
                        )
                    ),
                    "updated_at": data.get("updated_at", ""),
                    "created_at": data.get("created_at", ""),
                }
            )
        except (json.JSONDecodeError, OSError):
            continue
    saves.sort(key=lambda s: s.get("updated_at", ""), reverse=True)
    return saves


def has_saves() -> bool:
    return len(list_saves()) > 0


def unique_slug(name: str) -> str:
    base = slugify(name)
    slug = base
    n = 2
    while _save_path(slug).exists():
        slug = f"{base}-{n}"
        n += 1
    return slug


def slug_exists(slug: str) -> bool:
    return _save_path(slug).exists()


def save_team(slug: str, state: dict) -> None:
    ensure_saves_dir()
    state["slug"] = slug
    state["updated_at"] = _now_iso()
    if "created_at" not in state:
        state["created_at"] = state["updated_at"]
    with open(_save_path(slug), "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def load_team(slug: str) -> dict | None:
    path = _save_path(slug)
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def delete_team(slug: str) -> bool:
    path = _save_path(slug)
    if path.exists():
        path.unlink()
        return True
    return False
