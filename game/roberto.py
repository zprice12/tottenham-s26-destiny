"""Roberto de Zerbi comic-book speech with typewriter effect."""

from __future__ import annotations

import sys
import time

from game.ascii_art import print_face
from game.roberto_quips import pick_quip

BOX_PAD = 6  # spaces inside left/right borders beyond longest line


def _bubble_width(*lines: str, min_w: int = 40) -> int:
    content_w = max((len(line) for line in lines), default=0)
    return max(min_w, content_w + BOX_PAD * 2)


def _border(inner_w: int) -> str:
    return f"  +{'-' * (inner_w + 2)}+"


def _line(content: str, inner_w: int) -> str:
    return f"  | {content.ljust(inner_w)} |"


def _type_line(content: str, inner_w: int, delay: float) -> None:
    sys.stdout.write("  | ")
    for char in content:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write(" " * (inner_w - len(content)) + " |")
    print()


def say(lines: list[str], config: dict, show_face: bool = True) -> None:
    delay = config.get("roberto_typing_delay", 0.03)
    pause_line = config.get("roberto_pause_between_lines", 0.8)
    pause_bubble = config.get("roberto_pause_after_bubble", 1.2)

    inner_w = _bubble_width("Roberto de Zerbi:", *lines)

    if show_face:
        print()
        print_face()
        print()

    print(_border(inner_w))
    print(_line("Roberto de Zerbi:", inner_w))
    print(_border(inner_w))

    for line in lines:
        _type_line(line, inner_w, delay)
        time.sleep(pause_line)

    print(_border(inner_w))
    time.sleep(pause_bubble)


def say_quick(text: str) -> None:
    print(f"  [Roberto] {text}")


def maybe_react(
    action: str,
    config: dict,
    player: str = "",
    slot: str = "",
    position: str = "",
) -> None:
    """20% chance Roberto pops up with a quip about the move."""
    quip = pick_quip(action, player=player, slot=slot, position=position)
    if not quip:
        return
    quip_line = f'"{quip}"'
    print()
    print_face()
    inner_w = _bubble_width("Roberto de Zerbi:", quip_line)
    print(_border(inner_w))
    print(_line("Roberto de Zerbi:", inner_w))
    print(_line(quip_line, inner_w))
    print(_border(inner_w))
    time.sleep(config.get("roberto_pause_after_bubble", 1.2))
    print()
