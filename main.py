#!/usr/bin/env python3
"""Tottenham Hotspur Summer Squad Builder 2026 - entry point."""

from __future__ import annotations

import sys

from game import config as _cfg
from game.ascii_art import print_logo
from game.display import (
    clear_screen,
    formation_position_keys,
    render_command_bar,
    render_final_summary,
    render_grouped_player_picker,
    render_info_menu,
    render_intro,
    render_main_menu,
    render_main_view,
    render_market_filter_bar,
    render_player_directory,
    render_player_picker,
    render_position_key,
)
from game.formatting import fmt_m
from game.player import Player
from game.input_util import offer_skip_countdown
from game.roberto import maybe_react, say, say_quick
from game.roberto_quips import classify_lineup_move
from game.squad_manager import SquadManager
from game.team_saves import delete_team, has_saves, list_saves, unique_slug


def pause(msg: str = "Press Enter to continue...") -> None:
    input(f"\n  {msg}")


def pick_index(prompt: str, count: int, allow_zero: bool = True) -> int | None:
    if count == 0:
        print("  (none available)")
        return None
    while True:
        choice = input(f"  {prompt} (0 to cancel): ").strip()
        if allow_zero and choice == "0":
            return None
        try:
            idx = int(choice)
            if 1 <= idx <= count:
                return idx - 1
        except ValueError:
            pass
        print(f"  Enter 0-{count}.")


def resolve_position_filter(text: str, cfg: dict) -> str | None:
    """Return position key to filter, empty string to clear, or None if not a filter."""
    raw = text.strip().upper()
    if raw in ("*", "ALL"):
        return ""
    valid = set(formation_position_keys(cfg))
    if raw in valid:
        return raw
    return None


def pick_from_columnized_picker(
    title: str,
    entries: list[dict],
    cfg: dict,
    *,
    use_columns: bool = True,
) -> Player | None:
    """Pick a player by number; supports columns, pages, and position filters."""
    if not entries:
        print("  (none available)")
        return None

    position_filter = ""
    page = 0
    valid_positions = set(formation_position_keys(cfg))

    def visible_entries() -> list[dict]:
        if not position_filter:
            return entries
        return [e for e in entries if e["player"].position == position_filter]

    while True:
        visible = visible_entries()
        clear_screen()
        display_title = title
        if position_filter:
            display_title = f"{title} [{position_filter}]"
        if not visible:
            print(f"  {display_title}")
            print("  " + "-" * 66)
            print(f"  (no players at {position_filter})")
            print()
            render_market_filter_bar(cfg, position_filter)
            print("  0 = cancel")
            choice = input("  > ").strip()
            if choice == "0":
                return None
            filt = resolve_position_filter(choice, cfg)
            if filt is not None:
                position_filter = filt
                page = 0
            continue

        total_pages = render_player_picker(
            display_title, visible, page=page, use_columns=use_columns
        )
        print()
        if total_pages > 1:
            print(f"  Page {page + 1} of {total_pages}")
            nav = []
            if page > 0:
                nav.append("[P] Previous page")
            if page < total_pages - 1:
                nav.append("[N] Next page")
            if nav:
                print("  " + "   ".join(nav))
            print()
        render_market_filter_bar(cfg, position_filter)
        print()
        choice = input("  Player number (0 to cancel): ").strip()
        if choice == "0":
            return None
        choice_lower = choice.lower()
        if choice_lower == "n" and page < total_pages - 1:
            page += 1
            continue
        if choice_lower == "p" and page > 0:
            page -= 1
            continue
        filt = resolve_position_filter(choice, cfg)
        if filt is not None:
            position_filter = filt
            page = 0
            continue
        try:
            idx = int(choice)
            if 1 <= idx <= len(visible):
                return visible[idx - 1]["player"]
        except ValueError:
            pass
        pos_hint = ", ".join(sorted(valid_positions))
        print(f"  Enter 0-{len(visible)}, a position ({pos_hint}), * for all, or P/N for pages.")


def browse_player_directory(title: str, rows: list[tuple[Player, str]], cfg: dict) -> None:
    """Paginated read-only player table with position filtering."""
    if not rows:
        clear_screen()
        render_player_directory(title, rows)
        pause()
        return

    position_filter = ""
    page = 0
    total_pages = 1

    while True:
        visible = (
            rows
            if not position_filter
            else [(p, status) for p, status in rows if p.position == position_filter]
        )
        clear_screen()
        if not visible:
            print(f"  {title} [{position_filter}]")
            print("  (no players at this position)")
            print()
            render_market_filter_bar(cfg, position_filter)
            print("  0 = back")
            choice = input("  > ").strip()
            if choice == "0":
                return
            filt = resolve_position_filter(choice, cfg)
            if filt is not None:
                position_filter = filt
                page = 0
            continue

        total_pages = max(1, (len(visible) + 19) // 20)
        page = max(0, min(page, total_pages - 1))
        display_title = title
        if position_filter:
            display_title = f"{title} [{position_filter}]"
        if total_pages > 1:
            display_title = f"{display_title} — page {page + 1}/{total_pages}"
        total_pages = render_player_directory(display_title, visible, page=page)
        print()
        if total_pages > 1:
            print("  [N] Next   [P] Previous")
        render_market_filter_bar(cfg, position_filter)
        print("  0 = back")
        choice = input("  > ").strip()
        if choice == "0":
            return
        choice_lower = choice.lower()
        if choice_lower == "n" and page < total_pages - 1:
            page += 1
            continue
        if choice_lower == "p" and page > 0:
            page -= 1
            continue
        filt = resolve_position_filter(choice, cfg)
        if filt is not None:
            position_filter = filt
            page = 0
            continue


def prompt_squad_name() -> str | None:
    while True:
        name = input("  Enter a name for this squad build: ").strip()
        if name:
            return name
        print("  Please enter a name (e.g. 'Big Summer Overhaul').")


def run_intro(cfg: dict) -> None:
    render_intro()

    if offer_skip_countdown(5):
        say_quick("Let's get to work.")
        pause()
        return

    bubbles = [
        [
            "After that dreadful 2025/26 season...",
            "I need YOUR help this summer.",
            "You are Tottenham's sporting director.",
        ],
        [
            f"You start with {cfg['starting_budget_m']} million pounds.",
            "Sell players to raise funds. Buy from the market or buy back sold players.",
            f"Loan players out — +{int(cfg['loan_wage_savings_m'] + 0.5)}M budget "
            f"(+{int(cfg.get('academy_loan_wage_savings_m', 1) + 0.5)}M for academy).",
            "Keep an eye on budget and wages at the top of the screen.",
        ],
        [
            f"Roster: max {cfg['max_squad_size']} on the PITCH counting "
            f"(under-{cfg.get('roster_u21_exempt_age', 21)} exempt).",
            f"Non-homegrown: max {cfg['max_non_homegrown']} on the pitch "
            f"(U{cfg.get('roster_u21_exempt_age', 21)} exempt).",
            f"Sell up to {cfg['max_tottenham_sales']} from the current first-team squad.",
            "Loan returns? Sell as many as you like — doesn't count toward the 8.",
        ],
        [
            "Injured must be placed on pitch — cannot sell or loan.",
            "Loan returns: place, sell, or loan out before finishing.",
            "Left panel: Injured, loan returns, academy.",
            "Right panel: Sold and loaned out — buy back or recall from there.",
            "Pitch: 3 slots per position (a/b/c). Clear filled slots first.",
        ],
        [
            "And yes — every injured player will be fit by August.",
            "Lucky us! SO fortunate with injuries these past two seasons...",
            "Pick a player [P], buy from the market [B], check the squad [I].",
            "Finish when you're ready [F]. Exit to the menu [E].",
        ],
    ]
    for i, bubble in enumerate(bubbles):
        say(bubble, cfg, show_face=(i == 0))
    pause()


def run_welcome_back(manager: SquadManager, cfg: dict) -> None:
    clear_screen()
    status = "completed" if manager.completed else "in progress"
    say(
        [
            f"Welcome back to '{manager.team_name}'!",
            f"This build is {status}.",
            "Pick a player [P], buy [B], info [I], finish [F], or exit [E].",
        ],
        cfg,
    )
    pause()


def run_bissouma_option(manager: SquadManager, cfg: dict) -> None:
    clear_screen()
    say(
        [
            "One more thing before we carry on.",
            "Yves Bissouma's contract expired — but we hold a one-year option.",
            "Keep him? £60,000 per week. One year left. No transfer fee in or out.",
        ],
        cfg,
        show_face=True,
    )
    while True:
        choice = input("  Keep Bissouma for one more year? (y/n): ").strip().lower()
        if choice in ("y", "yes"):
            ok, msg = manager.add_bissouma()
            say_quick(msg if ok else f"Could not keep Bissouma: {msg}")
            pause()
            return
        if choice in ("n", "no"):
            say_quick("Understood. We move on without Bissouma.")
            pause()
            return
        print("  Enter y or n.")


def _maybe_offer_bissouma_option(manager: SquadManager, cfg: dict) -> None:
    if not manager.bissouma_option_pending:
        return
    manager.bissouma_option_pending = False
    manager.save()
    run_bissouma_option(manager, cfg)


def _pick_position_order(manager: SquadManager) -> str | None:
    render_position_key(manager.config)
    pos_input = input("  Position number (0 to cancel): ").strip()
    if pos_input == "0":
        return None
    try:
        order = int(pos_input)
    except ValueError:
        say_quick("Invalid position.")
        return None
    for pos in manager.config["formation"]:
        if pos["order"] == order:
            return pos["key"]
    say_quick("Invalid position.")
    return None


def _show_position_slots(manager: SquadManager, pos_key: str) -> None:
    letters = "abc"
    print(f"  Slots at {pos_key}:")
    for i in range(manager.config["slots_per_position"]):
        occupant = manager.get_slot_player(pos_key, i)
        if occupant:
            print(f"    {letters[i]}: {occupant.name}  (filled)")
        else:
            print(f"    {letters[i]}: ---  (open)")


def _handle_occupant(manager: SquadManager, occupant: Player, cfg: dict) -> bool:
    """Handle the player blocking a slot. Returns True if slot may now be free."""
    clear_screen()
    print(f"  Handle {occupant.name}  ({occupant.position})")
    print("  " + "-" * 40)

    options: list[tuple[str, str]] = [("Move to another position", "move")]
    if occupant.origin in ("injured", "loan_return", "academy"):
        options.append(("Return to sidebar", "return"))
    options.extend([
        ("Sell", "sell"),
        ("Loan out", "loan"),
    ])

    for i, (label, _) in enumerate(options, 1):
        print(f"  {i}. {label}")
    print("  0. Cancel")
    print()

    idx = pick_index("Choose action", len(options))
    if idx is None:
        return False

    action = options[idx][1]
    if action == "move":
        _place_player(manager, occupant, cfg, retry_label="continue moving")
        return True

    ok, msg = False, ""
    if action == "return":
        ok, msg = manager.remove_from_chart(occupant.depth_pos, occupant.depth_slot)
    elif action == "sell":
        ok, msg = manager.sell_player(occupant.id)
    elif action == "loan":
        ok, msg = manager.loan_out(occupant.id)

    say_quick(msg if ok else f"Blocked: {msg}")
    if ok and action == "sell":
        maybe_react("sell", cfg, player=occupant.name)
    elif ok and action == "loan":
        maybe_react("loan", cfg, player=occupant.name)
    if ok:
        pause()
        _maybe_offer_bissouma_option(manager, cfg)
    else:
        pause()
    return ok


def _resolve_filled_slot(
    manager: SquadManager,
    player: Player,
    pos_key: str,
    slot: int,
    cfg: dict,
) -> tuple[str, int] | None:
    """Prompt when target slot is filled. Returns new (pos_key, slot) or None."""
    letters = "abc"
    occupant = manager.get_slot_player(pos_key, slot)
    if not occupant:
        return pos_key, slot

    clear_screen()
    print(f"  Placing {player.name} at {pos_key}-{letters[slot]}")
    print(f"  That slot is occupied by {occupant.name}.")
    print()

    open_slots = manager.get_open_slots(pos_key)
    if open_slots:
        print(f"  Open slots at {pos_key}:")
        for s in open_slots:
            print(f"    {letters[s]}: ---")
        print()

    print("  What would you like to do?")
    print("  1. Pick an open slot at this position")
    print("  2. Handle the player currently in this slot")
    print("  0. Cancel and re-pick position")
    print()

    choice = input("  Choose (0-2): ").strip()
    if choice == "0":
        return None
    if choice == "1":
        if not open_slots:
            say_quick(f"No open slots at {pos_key}. Handle the occupant first.")
            pause()
            return _resolve_filled_slot(manager, player, pos_key, slot, cfg)
        if len(open_slots) == 1:
            return pos_key, open_slots[0]
        print()
        for i, s in enumerate(open_slots, 1):
            print(f"  {i}. Slot {letters[s]}")
        print("  0. Back")
        idx = pick_index("Open slot", len(open_slots), allow_zero=True)
        if idx is None:
            return _resolve_filled_slot(manager, player, pos_key, slot, cfg)
        return pos_key, open_slots[idx]
    if choice == "2":
        if _handle_occupant(manager, occupant, cfg):
            if not manager.slot_occupied(pos_key, slot, excluding=player.id):
                return pos_key, slot
            return _resolve_filled_slot(manager, player, pos_key, slot, cfg)
        return _resolve_filled_slot(manager, player, pos_key, slot, cfg)

    say_quick("Invalid choice.")
    pause()
    return _resolve_filled_slot(manager, player, pos_key, slot, cfg)


def _place_player(
    manager: SquadManager,
    player: Player,
    cfg: dict,
    retry_label: str = "placement",
) -> None:
    while True:
        pos_key = _pick_position_order(manager)
        if not pos_key:
            return

        _show_position_slots(manager, pos_key)
        slot_input = input("  Slot a/b/c (0 to re-pick position): ").strip().lower()
        if slot_input == "0":
            continue
        slot_map = {"a": 0, "b": 1, "c": 2}
        if slot_input not in slot_map:
            say_quick("Slot must be a, b, or c.")
            pause()
            continue
        slot = slot_map[slot_input]

        if manager.slot_occupied(pos_key, slot, excluding=player.id):
            resolved = _resolve_filled_slot(manager, player, pos_key, slot, cfg)
            if not resolved:
                continue
            pos_key, slot = resolved

        old_status = player.status
        was_on_chart = old_status == "depth_chart"
        old_slot = player.depth_slot if was_on_chart else -1
        old_pos = player.depth_pos if was_on_chart else ""

        ok, msg = manager.assign_to_chart(player.id, pos_key, slot)
        if ok:
            say_quick(msg)
            move_type = classify_lineup_move(
                old_status, old_slot, old_pos, pos_key, slot
            )
            maybe_react(
                move_type,
                cfg,
                player=player.name,
                slot="abc"[slot],
                position=pos_key,
            )
            pause()
            _maybe_offer_bissouma_option(manager, cfg)
            return
        say_quick(f"Could not complete {retry_label}: {msg}")
        pause()
        return


def _player_action_menu(manager: SquadManager, player: Player, cfg: dict) -> None:
    clear_screen()
    print(f"  {player.name}  ({player.position})")
    print("  " + "-" * 40)

    options: list[tuple[str, str]] = []

    if player.status == "sold":
        options.append(("Place on pitch (buy back)", "place"))
    elif player.status == "loaned_out":
        options.append(("Place on pitch (recall)", "place"))
    elif player.status == "injured":
        options.append(("Place on pitch", "place"))
    elif player.status in ("loan_return", "academy"):
        options.extend([
            ("Place on pitch", "place"),
            ("Sell", "sell"),
            ("Loan out", "loan"),
        ])
    elif player.status == "depth_chart":
        options.append(("Move to position", "place"))
        if player.depth_slot > 0:
            options.append(("Promote (up depth chart)", "promote"))
        if player.depth_slot < manager.config["slots_per_position"] - 1:
            options.append(("Demote (down depth chart)", "demote"))
        if player.origin in ("injured", "loan_return", "academy"):
            options.append(("Return to sidebar", "return"))
        options.extend([
            ("Sell", "sell"),
            ("Loan out", "loan"),
        ])

    for i, (label, _) in enumerate(options, 1):
        print(f"  {i}. {label}")
    print("  0. Cancel")
    print()

    idx = pick_index("Choose action", len(options))
    if idx is None:
        return

    action = options[idx][1]

    if action == "place":
        _place_player(manager, player, cfg)
        return

    ok, msg = False, ""
    if action == "return":
        ok, msg = manager.remove_from_chart(player.depth_pos, player.depth_slot)
    elif action == "promote":
        ok, msg = manager.promote_on_chart(player.id)
    elif action == "demote":
        ok, msg = manager.demote_on_chart(player.id)
    elif action == "sell":
        ok, msg = manager.sell_player(player.id)
    elif action == "loan":
        ok, msg = manager.loan_out(player.id)

    say_quick(msg if ok else f"Blocked: {msg}")
    if ok and action == "sell":
        maybe_react("sell", cfg, player=player.name)
    elif ok and action == "loan":
        maybe_react("loan", cfg, player=player.name)
    elif ok and action == "promote":
        maybe_react(
            "promote",
            cfg,
            player=player.name,
            slot="abc"[player.depth_slot],
            position=player.depth_pos,
        )
    elif ok and action == "demote":
        maybe_react(
            "demote",
            cfg,
            player=player.name,
            slot="abc"[player.depth_slot],
            position=player.depth_pos,
        )
    pause()
    if ok:
        _maybe_offer_bissouma_option(manager, cfg)


def cmd_pick_player(manager: SquadManager, cfg: dict) -> None:
    clear_screen()
    entries = manager.get_manageable_players()
    render_grouped_player_picker("PICK A PLAYER", entries)
    print()
    idx = pick_index("Player number", len(entries))
    if idx is None:
        return
    _player_action_menu(manager, entries[idx]["player"], cfg)


def cmd_buy_player(manager: SquadManager, cfg: dict) -> None:
    market = manager.get_market()
    entries = [{"player": p, "label": f"buy {fmt_m(p.buy_price_m)}"} for p in market]
    player = pick_from_columnized_picker(
        "TRANSFER MARKET — BUY A PLAYER",
        entries,
        cfg,
        use_columns=True,
    )
    if player is None:
        return
    _place_player(manager, player, cfg)


def cmd_view_info(manager: SquadManager, cfg: dict) -> None:
    while True:
        clear_screen()
        render_info_menu()
        choice = input("  Choose (0-2): ").strip()
        if choice == "0":
            return
        if choice == "1":
            clear_screen()
            render_player_directory(
                "MY SQUAD — all current players (HG = homegrown)",
                manager.get_directory_players(),
            )
            pause()
        elif choice == "2":
            market = manager.get_market()
            rows = [(p, "For sale") for p in market]
            browse_player_directory(
                "TRANSFER MARKET — players available to buy",
                rows,
                cfg,
            )
        else:
            say_quick("Enter 0, 1, or 2.")
            pause()


def cmd_finish(manager: SquadManager, cfg: dict) -> str:
    ok, issues = manager.can_finish()
    if not ok:
        say(["Hold on! We are not done yet..."] + issues, cfg, show_face=True)
        pause()
        return "continue"

    render_final_summary(manager)
    manager.save(mark_completed=True)
    say_quick(f"'{manager.team_name}' saved as complete. Re-edit anytime from the main menu.")
    pause("Press Enter to return to main menu...")
    return "menu"


def squad_session_loop(manager: SquadManager, cfg: dict, is_new: bool) -> None:
    if is_new:
        run_intro(cfg)
    else:
        run_welcome_back(manager, cfg)

    while True:
        render_main_view(manager)
        render_command_bar()
        choice = input("  > ").strip().lower()

        if choice in ("p", "pick"):
            cmd_pick_player(manager, cfg)
        elif choice in ("b", "buy"):
            cmd_buy_player(manager, cfg)
        elif choice in ("i", "info"):
            cmd_view_info(manager, cfg)
        elif choice in ("f", "finish"):
            result = cmd_finish(manager, cfg)
            if result == "menu":
                return
        elif choice in ("e", "exit"):
            manager.save()
            say_quick(f"'{manager.team_name}' saved.")
            pause("Press Enter for main menu...")
            return
        else:
            say_quick("Use P = pick, B = buy, I = info, F = finish, E = exit.")
            pause()


def create_new_squad(cfg: dict) -> None:
    clear_screen()
    print_logo()
    print()
    print("  CREATE A NEW SQUAD BUILD")
    print()
    name = prompt_squad_name()
    if not name:
        return
    slug = unique_slug(name)
    manager = SquadManager.new_game(name, slug)
    squad_session_loop(manager, cfg, is_new=True)


def edit_existing_squad(cfg: dict, saves: list[dict]) -> None:
    clear_screen()
    print("  SELECT A SQUAD TO EDIT")
    print("  " + "-" * 50)
    for i, s in enumerate(saves, 1):
        status = "Complete" if s["completed"] else "In Progress"
        print(f"  {i:>2}. {s['name']:<30} [{status}]")
    print()
    idx = pick_index("Squad number", len(saves))
    if idx is None:
        return
    slug = saves[idx]["slug"]
    manager = SquadManager.load_game(slug)
    if not manager:
        say_quick("Could not load that squad.")
        pause()
        return
    squad_session_loop(manager, cfg, is_new=False)


def delete_saved_squad(saves: list[dict]) -> None:
    clear_screen()
    print("  DELETE A SAVED SQUAD")
    print("  " + "-" * 50)
    for i, s in enumerate(saves, 1):
        print(f"  {i:>2}. {s['name']}")
    print()
    idx = pick_index("Squad number", len(saves))
    if idx is None:
        return
    name = saves[idx]["name"]
    confirm = input(f"  Delete '{name}'? This cannot be undone. (y/n): ").strip().lower()
    if confirm in ("y", "yes"):
        delete_team(saves[idx]["slug"])
        say_quick(f"Deleted '{name}'.")
    else:
        say_quick("Deletion cancelled.")
    pause()


def run_main_menu(cfg: dict) -> bool:
    saves = list_saves()
    render_main_menu(saves)

    if saves:
        choice = input("  Choose option: ").strip()
        if choice == "1":
            edit_existing_squad(cfg, saves)
        elif choice == "2":
            create_new_squad(cfg)
        elif choice == "3":
            delete_saved_squad(saves)
        elif choice == "0":
            return False
        else:
            say_quick("Unknown option.")
            pause()
    else:
        input("  Press Enter to create your first squad...")
        create_new_squad(cfg)

    return True


def main() -> None:
    cfg = _cfg.load_config()
    try:
        clear_screen()
        print_logo()
        print()
        if has_saves():
            print("  Welcome back to Tottenham Summer Squad Builder 2026!")
            pause("Press Enter for the main menu...")
        else:
            print("  Welcome to Tottenham Summer Squad Builder 2026!")
            pause("Press Enter to get started...")

        while run_main_menu(cfg):
            pass

        print()
        print("  Roberto says: 'Arrivederci. COYS!'")
        print()
    except KeyboardInterrupt:
        print("\n\n  Roberto says: 'We will finish the squad another day.'")
        sys.exit(0)


if __name__ == "__main__":
    main()
