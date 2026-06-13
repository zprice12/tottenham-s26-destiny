"""Load ASCII art from repo text files."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"


def _load_lines(filename: str) -> list[str]:
    path = ASSETS / filename
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return [line.rstrip("\n") for line in f.readlines()]


def _width(lines: list[str]) -> int:
    return max((len(line) for line in lines), default=0)


LOGO_LINES = _load_lines("logo.txt")
LOGO_SMALL_LINES = LOGO_LINES  # same asset; compact enough for header
ROBERTO_FACE_LINES = _load_lines("roberto_face.txt")
ROBERTO_STANDING_LINES = _load_lines("roberto_standing.txt")

LOGO_WIDTH = _width(LOGO_LINES)
ROBERTO_STANDING_WIDTH = _width(ROBERTO_STANDING_LINES)
ROBERTO_FACE_WIDTH = _width(ROBERTO_FACE_LINES)

# Legacy string exports for anything still importing
TOTTENHAM_CREST = "\n".join(LOGO_LINES) if LOGO_LINES else ""
TOTTENHAM_CREST_SMALL = TOTTENHAM_CREST
ROBERTO_FACE = "\n".join(ROBERTO_FACE_LINES) if ROBERTO_FACE_LINES else ""

CELEBRATION_BANNER = r"""
  *   *   *   *   *   *   *   *   *   *   *   *   *   *
  *                                                 *
  *     S Q U A D   B U I L D   C O M P L E T E     *
  *                                                 *
  *   *   *   *   *   *   *   *   *   *   *   *   *   *
"""

SCREENSHOT_BANNER = r"""
  +=====================================================+
  |                                                     |
  |   SCREENSHOT THIS!  YOUR 2026/27 SQUAD IS READY!    |
  |                                                     |
  +=====================================================+
"""


def print_logo(indent: str = "  ") -> None:
    for line in LOGO_LINES:
        print(f"{indent}{line}")


def print_face(indent: str = "  ") -> None:
    for line in ROBERTO_FACE_LINES:
        print(f"{indent}{line}")


def standing_lines_padded(width: int) -> list[str]:
    return [line[:width].ljust(width) for line in ROBERTO_STANDING_LINES]
