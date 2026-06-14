"""Cross-platform key input for intro skip countdown."""

from __future__ import annotations

import math
import os
import sys
import time

SKIP_KEYS = frozenset({"ENTER", "S", "SKIP", "RIGHT", "SPACE"})


def _read_key_unix(timeout: float) -> str | None:
    import select
    import termios
    import tty

    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        ready, _, _ = select.select([sys.stdin], [], [], timeout)
        if not ready:
            return None
        ch = sys.stdin.read(1)
        if ch == "\x1b":
            seq = ""
            for _ in range(2):
                r, _, _ = select.select([sys.stdin], [], [], 0.05)
                if r:
                    seq += sys.stdin.read(1)
            if seq == "[C":
                return "RIGHT"
            return None
        if ch in ("\r", "\n"):
            return "ENTER"
        if ch == " ":
            return "SPACE"
        if ch.lower() == "s":
            return "S"
        return None
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def _read_key_windows(timeout: float) -> str | None:
    import msvcrt

    end = time.monotonic() + timeout
    while time.monotonic() < end:
        if msvcrt.kbhit():
            ch = msvcrt.getch()
            if ch in (b"\x00", b"\xe0"):
                ch2 = msvcrt.getch()
                if ch2 == b"M":
                    return "RIGHT"
                if ch2 == b"K":
                    return "SKIP"
                return None
            if ch in (b"\r", b"\n"):
                return "ENTER"
            if ch == b" ":
                return "SPACE"
            if ch.lower() == b"s":
                return "S"
        time.sleep(0.05)
    return None


def read_key_wait(timeout: float) -> str | None:
    if os.name == "nt":
        return _read_key_windows(timeout)
    return _read_key_unix(timeout)


def offer_skip_countdown(seconds: int = 5) -> bool:
    """
    Countdown before intro. Returns True if user skips.
    Accepts ENTER, S, SPACE, or right arrow.
    """
    if not sys.stdin.isatty():
        print()
        print(f"  Starting intro in {seconds} seconds...")
        time.sleep(seconds)
        return False

    print()
    print("  Roberto de Zerbi is about to explain the rules...")
    print()

    deadline = time.monotonic() + seconds
    last_tick = -1

    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            print("\r  Starting intro..." + " " * 40)
            print()
            return False

        tick = max(1, math.ceil(remaining))
        if tick != last_tick:
            last_tick = tick
            print(
                f"\r  Press ENTER or S to skip  |  starting in {tick}...   ",
                end="",
                flush=True,
            )

        key = read_key_wait(0.1)
        if key in SKIP_KEYS:
            print("\r  Intro skipped." + " " * 40)
            print()
            return True
