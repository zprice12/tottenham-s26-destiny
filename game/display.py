"""Terminal display: spatial pitch with left/right sidebars."""

from __future__ import annotations

import os

from game.ascii_art import (
    CELEBRATION_BANNER,
    ROBERTO_STANDING_WIDTH,
    SCREENSHOT_BANNER,
    print_logo,
    standing_lines_padded,
)
from game.formatting import fmt_m
from game.player import Player
from game.squad_manager import SquadManager

# Sidebars
LEFT_W = 28
RIGHT_W = max(28, ROBERTO_STANDING_WIDTH + 2)

PITCH_W = 86
NAME_W = 18
BLOCK_W = NAME_W + 3  # " a:" + name
INNER_LEFT = 1
INNER_WIDTH = PITCH_W - 2  # playable width between side | borders

GOAL_W = 14
GOAL_DEPTH = 3  # rows into pitch; row 0 / last row = goal line on field border

BLOCK_ROWS = 4  # label + a/b/c slots
GAP_LINES = 3   # empty rows between forward / mid / defence lines
GK_GAP = 2      # empty rows between defence line and GK

ROW_FORWARDS = GOAL_DEPTH + 4
ROW_MIDFIELD = ROW_FORWARDS + BLOCK_ROWS + GAP_LINES
ROW_DEFENCE = ROW_MIDFIELD + BLOCK_ROWS + GAP_LINES
ROW_GK = ROW_DEFENCE + BLOCK_ROWS + GK_GAP

# Gap from goal crossbar to nearest outfield line (same at top and bottom)
GAP_GOAL_TO_LINE = ROW_FORWARDS - GOAL_DEPTH - 1
BOTTOM_CROSSBAR_ROW = ROW_GK + BLOCK_ROWS + GAP_GOAL_TO_LINE
PITCH_ROWS = BOTTOM_CROSSBAR_ROW + GOAL_DEPTH + 1


def _even_cols(count: int) -> list[int]:
    """Center a row of blocks with equal padding to both side borders."""
    group_w = count * BLOCK_W
    side_pad = (INNER_WIDTH - group_w) // 2
    start = INNER_LEFT + side_pad
    return [start + i * BLOCK_W for i in range(count)]


def _build_pitch_layout() -> dict[str, tuple[int, int]]:
    fwd = _even_cols(3)
    mid = _even_cols(3)
    defence = _even_cols(4)
    gk = _even_cols(1)[0]
    return {
        "LW": (ROW_FORWARDS, fwd[0]),
        "ST": (ROW_FORWARDS, fwd[1]),
        "RW": (ROW_FORWARDS, fwd[2]),
        "LCM": (ROW_MIDFIELD, mid[0]),
        "CAM": (ROW_MIDFIELD, mid[1]),
        "RCM": (ROW_MIDFIELD, mid[2]),
        "LB": (ROW_DEFENCE, defence[0]),
        "LCB": (ROW_DEFENCE, defence[1]),
        "RCB": (ROW_DEFENCE, defence[2]),
        "RB": (ROW_DEFENCE, defence[3]),
        "GK": (ROW_GK, gk),
    }


PITCH_LAYOUT = _build_pitch_layout()


def clear_screen() -> None:
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def _player_slot_name(manager: SquadManager, pos_key: str, slot: int) -> str:
    pid = manager.depth_chart.get(pos_key, [None, None, None])[slot]
    if pid and pid in manager.players:
        return manager.players[pid].short_name(NAME_W)
    return "---"


def _position_block(manager: SquadManager, pos_key: str) -> list[str]:
    label = f" {pos_key:^{BLOCK_W - 2}} "
    lines = [label[:BLOCK_W].ljust(BLOCK_W)]
    for i, letter in enumerate("abc"):
        name = _player_slot_name(manager, pos_key, i)
        row = f" {letter}:{name:<{NAME_W}}"
        lines.append(row.ljust(BLOCK_W)[:BLOCK_W])
    return lines


def _goal_posts() -> tuple[int, int]:
    left = INNER_LEFT + (INNER_WIDTH - GOAL_W) // 2
    return left, left + GOAL_W - 1


def _draw_top_goal(grid: list[list[str]]) -> None:
    """Top goal: back wall on top border, crossbar facing the field."""
    left, right = _goal_posts()
    cross = GOAL_DEPTH

    grid[0][left] = "+"
    grid[0][right] = "+"
    for c in range(left + 1, right):
        grid[0][c] = "-"

    for r in range(1, cross):
        grid[r][left] = "|"
        grid[r][right] = "|"

    grid[cross][left] = "+"
    grid[cross][right] = "+"
    for c in range(left + 1, right):
        grid[cross][c] = "-"


def _draw_bottom_goal(grid: list[list[str]]) -> None:
    """Bottom goal: back wall on bottom border, crossbar facing the field."""
    left, right = _goal_posts()
    last = PITCH_ROWS - 1
    cross = BOTTOM_CROSSBAR_ROW

    grid[last][left] = "+"
    grid[last][right] = "+"
    for c in range(left + 1, right):
        grid[last][c] = "-"

    for r in range(cross + 1, last):
        grid[r][left] = "|"
        grid[r][right] = "|"

    grid[cross][left] = "+"
    grid[cross][right] = "+"
    for c in range(left + 1, right):
        grid[cross][c] = "-"


def _draw_goals(grid: list[list[str]]) -> None:
    _draw_top_goal(grid)
    _draw_bottom_goal(grid)


def _build_pitch_grid(manager: SquadManager) -> list[str]:
    grid = [[" "] * PITCH_W for _ in range(PITCH_ROWS)]

    for row in range(PITCH_ROWS):
        if row == 0 or row == PITCH_ROWS - 1:
            for col in range(PITCH_W):
                grid[row][col] = "-"
        else:
            grid[row][0] = "|"
            grid[row][PITCH_W - 1] = "|"

    grid[0][0] = grid[0][PITCH_W - 1] = "+"
    grid[PITCH_ROWS - 1][0] = grid[PITCH_ROWS - 1][PITCH_W - 1] = "+"

    _draw_goals(grid)

    for pos_key, (start_row, start_col) in PITCH_LAYOUT.items():
        block = _position_block(manager, pos_key)
        for dr, line in enumerate(block):
            for dc, ch in enumerate(line[:BLOCK_W]):
                r, c = start_row + dr, start_col + dc
                if 0 < r < PITCH_ROWS - 1 and 0 < c < PITCH_W - 1:
                    grid[r][c] = ch

    return ["".join(row) for row in grid]


def _sidebar_section(title: str, players: list[Player], width: int) -> list[str]:
    lines = [title[:width], "-" * width]
    if players:
        for p in players:
            lines.append(p.short_name(width)[:width])
    else:
        lines.append("(none)"[:width])
    lines.append("")
    return lines


def _build_left_sidebar(manager: SquadManager) -> list[str]:
    sections = [
        _sidebar_section("INJURED", manager.get_injured(), LEFT_W),
        _sidebar_section("LOAN RETURNS", manager.get_loan_returns(), LEFT_W),
        _sidebar_section("ACADEMY", manager.get_academy(), LEFT_W),
    ]
    lines: list[str] = []
    for section in sections:
        lines.extend(section)
    return lines


def _build_right_sidebar(manager: SquadManager, target_height: int | None = None) -> list[str]:
    sections = [
        _sidebar_section("SOLD", manager.get_sold(), RIGHT_W),
        _sidebar_section("LOANED OUT", manager.get_loaned_out(), RIGHT_W),
    ]
    top: list[str] = []
    for section in sections:
        top.extend(section)

    roberto = standing_lines_padded(RIGHT_W)
    lines = top + [""] + roberto

    if target_height is not None:
        gap = target_height - len(lines)
        if gap > 0:
            lines = top + [""] * (gap - len(roberto)) + roberto
        elif gap < 0:
            keep = max(0, target_height - len(roberto) - 1)
            lines = top[:keep] + [""] + roberto

    return lines


def _pad_lines(lines: list[str], height: int, width: int) -> list[str]:
    padded = [l[:width].ljust(width) for l in lines]
    while len(padded) < height:
        padded.append(" " * width)
    return padded[:height]


def _print_layout(left: list[str], pitch: list[str], right: list[str]) -> None:
    height = max(len(left), len(pitch), len(right))
    left = _pad_lines(left, height, LEFT_W)
    pitch = _pad_lines(pitch, height, PITCH_W)
    right = _pad_lines(right, height, RIGHT_W)
    gap = " "
    for l, m, r in zip(left, pitch, right):
        print(f"{l}{gap}{m}{gap}{r}")


def _render_warnings(warnings: list[str]) -> None:
    if not warnings:
        return
    width = 72
    print("  " + "=" * width)
    print("  NEEDS RESOLUTION  —  fix these before you can finish the squad")
    print("  " + "=" * width)
    for warning in warnings:
        print(f"  >> {warning}")
    print("  " + "=" * width)


def render_header(manager: SquadManager) -> None:
    print_logo()
    squad_label = manager.team_name or "Unnamed Squad"
    status = "COMPLETE" if manager.completed else "IN PROGRESS"
    print("  TOTTENHAM HOTSPUR FC  |  Summer Squad Builder 2026")
    print(f"  Squad: {squad_label}  [{status}]")
    print(
        f"  Budget: {fmt_m(manager.budget_m)}  |  "
        f"Players: {manager.roster_count()}/{manager.config['max_squad_size']}  |  "
        f"Non-HG: {manager.non_homegrown_count()}/{manager.config['max_non_homegrown']}  |  "
        f"Sales: {manager.tottenham_sales_count}/{manager.config['max_tottenham_sales']}"
    )
    _render_warnings(manager.get_warnings())
    print(f"  Wages: {manager.total_wages_m_rounded()}M/yr")
    print()


def render_main_view(manager: SquadManager) -> None:
    if manager.config.get("screen_clear_on_redraw", True):
        clear_screen()

    render_header(manager)
    pitch = _build_pitch_grid(manager)
    _print_layout(
        _build_left_sidebar(manager),
        pitch,
        _build_right_sidebar(manager, len(pitch)),
    )
    print()


def render_command_bar() -> None:
    print("  COMMANDS:")
    print("  [P] Pick a player   [B] Buy   [I] Player info   [F] Finish   [E] Exit")
    print()


def render_main_menu(saves: list[dict]) -> None:
    clear_screen()
    print_logo()
    print()
    print("  TOTTENHAM HOTSPUR FC")
    print("  Summer Squad Builder 2026 — Main Menu")
    print()
    if saves:
        print("  YOUR SAVED SQUADS:")
        print("  " + "-" * 60)
        for i, s in enumerate(saves, 1):
            status = "Complete" if s["completed"] else "In Progress"
            print(
                f"  {i:>2}. {s['name']:<28} {status:<12} "
                f"{fmt_m(s['budget_m'])}  ({s['squad_count']} players)"
            )
        print()
    print("  MAIN MENU:")
    if saves:
        print("   1. Edit an existing squad")
        print("   2. Create a new squad")
        print("   3. Delete a saved squad")
    else:
        print("   (No saved squads yet — you'll create your first one next.)")
    print("   0. Exit")
    print()


def render_intro() -> None:
    clear_screen()
    print_logo()
    print()


def render_position_key(config: dict) -> None:
    print("  POSITIONS:")
    for pos in sorted(config["formation"], key=lambda x: x["order"]):
        print(f"    {pos['order']:>2}. {pos['key']:<4} - {pos['label']}")
    print("    Slots: a = starter, b = 2nd, c = 3rd")
    print("    Filled slots must be cleared before placing another player there.")
    print()


def render_player_directory(title: str, rows: list[tuple[Player, str]]) -> None:
    print(f"  {title}")
    print("  " + "-" * 118)
    print(
        "  "
        f"{'Name':<22} {'Pos':<4} {'Age':>3}  {'Nationality':<14} "
        f"{'HG':<5} {'Sale':>6}  {'Buy':>6}  {'Wages':>12}  "
        f"{'Ctr':>4}  {'Status':<16} Notes"
    )
    print("  " + "-" * 118)
    if not rows:
        print("  (none)")
        return
    for player, status in rows:
        print(f"  {player.info_line(status)}")


def render_info_menu() -> None:
    print("  PLAYER INFO")
    print("  " + "-" * 40)
    print("  1. My squad (all current players)")
    print("  2. Transfer market (players to buy)")
    print("  0. Back")
    print()


def render_player_picker(title: str, entries: list[dict]) -> None:
    print(f"  {title}")
    print("  " + "-" * 66)
    if not entries:
        print("  (none)")
        return
    for i, entry in enumerate(entries, 1):
        p = entry["player"]
        label = entry.get("label", "")
        print(f"  {i:>2}. {p.name:<24} {label}")


def render_final_summary(manager: SquadManager) -> None:
    clear_screen()
    print_logo()
    print(CELEBRATION_BANNER)
    print()
    print(f"  Squad: {manager.team_name}")
    print("  Roberto de Zerbi says:")
    print('  "Bravo! This is the squad we take into 2026/27. COYS!"')
    print()
    print("  STARTING XI (4-3-3)")
    print("  " + "-" * 50)

    for pos in manager.config["formation"]:
        pid = manager.depth_chart.get(pos["key"], [None, None, None])[0]
        if pid and pid in manager.players:
            p = manager.players[pid]
            print(f"  {pos['key']:<4}  {p.name}")
        else:
            print(f"  {pos['key']:<4}  ---")

    print()
    print("  FULL ROSTER (on pitch)")
    print("  " + "-" * 72)
    for p in sorted(manager.get_on_pitch(), key=lambda x: (x.depth_pos, x.depth_slot, x.name)):
        slot = "abc"[p.depth_slot]
        print(f"  {p.display_line()}  [{p.depth_pos}-{slot}]")

    print()
    print("  FINANCIAL SUMMARY")
    print("  " + "-" * 50)
    print(f"  Budget remaining:     {fmt_m(manager.budget_m)}")
    print(f"  Annual wage bill:     {manager.total_wages_m_rounded()}M")
    print(f"  Tottenham sales used: {manager.tottenham_sales_count}/{manager.config['max_tottenham_sales']}")

    bought = [p for p in manager.players.values() if p.origin == "market" and p.status == "depth_chart"]
    sold = [p for p in manager.players.values() if p.status == "sold"]
    loaned = [p for p in manager.players.values() if p.status == "loaned_out"]

    print()
    print("  TRANSFERS")
    print("  " + "-" * 50)
    print(f"  Players bought:  {len(bought)}")
    for p in bought:
        print(f"    + {p.name} ({fmt_m(p.buy_price_m)})")
    print(f"  Players sold:    {len(sold)}")
    for p in sold:
        print(f"    - {p.name} ({fmt_m(p.sale_price_m)})")
    print(f"  Players loaned:  {len(loaned)}")
    for p in loaned:
        print(f"    ~ {p.name}")

    print()
    print(SCREENSHOT_BANNER)
    print()
