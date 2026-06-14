#!/usr/bin/env python3
"""Exhaustive game logic tests — run: python3 tests/test_game_logic.py"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from game.player import WEEKS_PER_YEAR
from game.squad_manager import SquadManager, WAGE_BILL_STATUSES

PASS = 0
FAIL = 0


def ok(cond: bool, msg: str) -> None:
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS: {msg}")
    else:
        FAIL += 1
        print(f"  FAIL: {msg}")


def assert_eq(got, expected, msg: str) -> None:
    ok(got == expected, f"{msg} (got {got!r}, expected {expected!r})")


def assert_true(cond, msg: str) -> None:
    ok(bool(cond), msg)


def manual_wage_bill(mgr: SquadManager) -> int:
    return sum(
        p.wages_per_week * WEEKS_PER_YEAR
        for p in mgr.players.values()
        if p.status in WAGE_BILL_STATUSES
    )


def depth_chart_ids(mgr: SquadManager) -> list[str]:
    ids: list[str] = []
    for slots in mgr.depth_chart.values():
        for pid in slots:
            if pid:
                ids.append(pid)
    return ids


def no_duplicates_on_pitch(mgr: SquadManager, label: str) -> None:
    ids = depth_chart_ids(mgr)
    assert_eq(len(ids), len(set(ids)), f"{label}: no duplicate player ids on pitch")


def fresh() -> SquadManager:
    import uuid
    slug = f"test-{uuid.uuid4().hex[:8]}"
    return SquadManager.new_game("Test Squad", slug)


def test_initial_state():
    print("\n=== Initial state ===")
    mgr = fresh()
    assert_eq(mgr.budget_m, 100.0, "starting budget 100M")
    assert_true(mgr.tottenham_sales_count == 0, "sales count starts at 0")
    no_duplicates_on_pitch(mgr, "initial")
    assert_eq(mgr.depth_chart["GK"][0], "gka", "Vicario at GK-a via gka id")
    assert_eq(len(mgr.get_on_pitch()), 22, "22 squad players on pitch from CSV")
    assert_eq(mgr.roster_count() + mgr.u21_exempt_count(), len(mgr.get_on_pitch()),
              "on-pitch equals counted + u21 exempt")
    assert_eq(mgr.annual_wage_bill_pounds(), manual_wage_bill(mgr), "wage bill matches manual")
    assert_eq(mgr.total_wages_m_rounded(), int(mgr.total_wages_m() + 0.5), "wage rounding")
    # injured/academy not on pitch — should not affect roster count
    inj = len(mgr.get_injured())
    acad = len(mgr.get_academy())
    assert_true(inj > 0 and acad > 0, "injured and academy exist in sidebar")
    assert_eq(mgr.roster_count(), len([p for p in mgr.get_on_pitch() if p.age >= 21]),
              "roster count is 21+ on pitch only")


def test_budget_sell_buyback():
    print("\n=== Budget: sell & buy back ===")
    mgr = fresh()
    p = mgr.players["gkb"]
    price = p.sale_price_m
    b0 = mgr.budget_m
    ok, _ = mgr.sell_player(p.id)
    assert_true(ok, "sell squad player")
    assert_eq(mgr.budget_m, b0 + price, "budget increased by sale price")
    assert_eq(mgr.tottenham_sales_count, 1, "sales count incremented")
    assert_true(p.id not in [x.id for x in mgr.players_on_wage_bill()], "sold player off wage bill")
    w_before = mgr.annual_wage_bill_pounds()
    ok, _ = mgr.assign_to_chart(p.id, "GK", 1)
    assert_true(ok, "buy back to GK-b")
    assert_eq(mgr.budget_m, b0 + price - price, "buy back costs sale price")
    assert_eq(mgr.tottenham_sales_count, 0, "sales count decremented on buy back")
    assert_true(mgr.annual_wage_bill_pounds() > w_before, "wages back on books after buy back")
    no_duplicates_on_pitch(mgr, "after buy back")


def test_budget_loan():
    print("\n=== Budget: loan ===")
    mgr = fresh()
    lr = mgr.get_loan_returns()[0]
    b0 = mgr.budget_m
    w0 = manual_wage_bill(mgr)
    ok, _ = mgr.loan_out(lr.id)
    assert_true(ok, "loan loan return")
    assert_eq(mgr.budget_m, b0 + 2, "loan return adds 2M to budget")
    assert_eq(mgr.annual_wage_bill_pounds(), w0 - lr.wages_per_week * WEEKS_PER_YEAR,
              "loan return wages removed")
    acad = mgr.get_academy()[0]
    b1 = mgr.budget_m
    ok, _ = mgr.loan_out(acad.id)
    assert_true(ok, "loan academy")
    assert_eq(mgr.budget_m, b1 + 1, "academy loan adds 1M")


def test_budget_market_buy():
    print("\n=== Budget: market buy ===")
    mgr = fresh()
    market = mgr.get_market()[0]
    b0 = mgr.budget_m
    open_pos = "RW"
    slot = 0
    for s in range(3):
        if not mgr.depth_chart[open_pos][s]:
            slot = s
            break
    ok, _ = mgr.assign_to_chart(market.id, open_pos, slot)
    assert_true(ok, "buy from market")
    assert_eq(mgr.budget_m, b0 - market.buy_price_m, "budget reduced by buy price")
    assert_true(market.id in depth_chart_ids(mgr), "bought player on pitch")
    no_duplicates_on_pitch(mgr, "after market buy")


def test_injured_rules():
    print("\n=== Injured: cannot sell/loan, can place ===")
    mgr = fresh()
    inj = mgr.get_injured()[0]
    ok, msg = mgr.sell_player(inj.id)
    assert_true(not ok and "cannot be sold" in msg, "injured cannot sell")
    ok, msg = mgr.loan_out(inj.id)
    assert_true(not ok and "cannot be loaned" in msg, "injured cannot loan")
    w0 = mgr.annual_wage_bill_pounds()
    roster0 = mgr.roster_count()
    slot = 2
    for pos in mgr.config["formation"]:
        if mgr.depth_chart[pos["key"]][slot] is None:
            ok, _ = mgr.assign_to_chart(inj.id, pos["key"], slot)
            assert_true(ok, f"place injured at {pos['key']}-c")
            break
    assert_true(mgr.annual_wage_bill_pounds() == w0, "injured already on wage bill")
    assert_true(mgr.roster_count() >= roster0, "injured on pitch counts if 21+")


def find_open_slot(mgr: SquadManager, pos_key: str | None = None) -> tuple[str, int]:
    positions = [pos_key] if pos_key else [p["key"] for p in mgr.config["formation"]]
    for key in positions:
        for slot in mgr.get_open_slots(key):
            return key, slot
    raise RuntimeError("no open slot")


def place_all_injured(mgr: SquadManager) -> None:
    for inj in list(mgr.get_injured()):
        pos, slot = find_open_slot(mgr)
        ok, msg = mgr.assign_to_chart(inj.id, pos, slot)
        if not ok:
            raise RuntimeError(f"could not place injured {inj.name}: {msg}")


def loan_out_all_returns(mgr: SquadManager) -> None:
    for lr in list(mgr.get_loan_returns()):
        ok, msg = mgr.loan_out(lr.id)
        if not ok:
            raise RuntimeError(f"could not loan out {lr.name}: {msg}")


def place_all_loan_returns(mgr: SquadManager) -> None:
    for lr in list(mgr.get_loan_returns()):
        try:
            pos, slot = find_open_slot(mgr)
            ok, msg = mgr.assign_to_chart(lr.id, pos, slot)
            if not ok:
                raise RuntimeError(f"could not place {lr.name}: {msg}")
        except RuntimeError:
            ok, msg = mgr.sell_player(lr.id)
            if not ok:
                ok, msg = mgr.loan_out(lr.id)
            if not ok:
                raise RuntimeError(f"could not resolve {lr.name}: {msg}")


def sell_down_to_finish_limits(mgr: SquadManager) -> None:
    while mgr.roster_count() > mgr.config["max_squad_size"] or (
        mgr.non_homegrown_count() > mgr.config["max_non_homegrown"]
    ):
        candidates = [
            p for p in mgr.get_on_pitch()
            if p.age >= 21 and mgr.counts_toward_roster_limit(p)
        ]
        non_hg = [p for p in candidates if mgr.counts_toward_non_hg_limit(p)]
        pool = non_hg if non_hg and mgr.non_homegrown_count() > mgr.config["max_non_homegrown"] else candidates
        if not pool:
            break
        ok, msg = mgr.sell_player(pool[0].id)
        if not ok:
            raise RuntimeError(f"could not sell {pool[0].name}: {msg}")


def make_finishable_loan_returns_out(mgr: SquadManager) -> None:
    place_all_injured(mgr)
    loan_out_all_returns(mgr)


def make_finishable_place_all_then_trim(mgr: SquadManager) -> None:
    place_all_injured(mgr)
    place_all_loan_returns(mgr)
    sell_down_to_finish_limits(mgr)


def finish_and_save(mgr: SquadManager) -> None:
    ok, issues = mgr.can_finish()
    if not ok:
        raise RuntimeError(f"expected finishable squad, got: {issues}")
    mgr.save(mark_completed=True)


def test_move_player_no_duplicate():
    print("\n=== Move player between slots ===")
    mgr = fresh()
    p = mgr.players["sta"]
    assert_eq(p.depth_pos, "ST", "Solanke starts ST")
    pos, slot = find_open_slot(mgr, "LW")
    ok, msg = mgr.assign_to_chart(p.id, pos, slot)
    assert_true(ok, f"move Solanke to {pos}-{('abc')[slot]} ({msg})")
    assert_eq(mgr.depth_chart["ST"][0], None, "old ST-a slot cleared")
    assert_eq(mgr.depth_chart[pos][slot], p.id, f"now at {pos}")
    no_duplicates_on_pitch(mgr, "after move")


def test_occupied_slot_blocked():
    print("\n=== Occupied slot blocked ===")
    mgr = fresh()
    a, b = mgr.players["sta"], mgr.players["stb"]
    ok, msg = mgr.assign_to_chart(b.id, "ST", 0)
    assert_true(not ok and "occupied" in msg.lower(), "cannot place into occupied slot")


def test_sales_limit():
    print("\n=== Sales limit (squad origin only) ===")
    mgr = fresh()
    squad_on_pitch = [p for p in mgr.get_on_pitch() if p.origin == "squad" and p.age >= 21]
    sold = 0
    for p in squad_on_pitch[:9]:
        ok, _ = mgr.sell_player(p.id)
        if ok:
            sold += 1
    assert_eq(mgr.tottenham_sales_count, min(8, sold), "max 8 sales counted")
    if sold >= 8:
        remaining = [p for p in mgr.get_on_pitch() if p.origin == "squad"]
        if remaining:
            ok, msg = mgr.sell_player(remaining[0].id)
            assert_true(not ok and "8 players" in msg, "9th squad sale blocked")


def test_loan_return_sell_no_limit():
    print("\n=== Loan return sell does not count toward 8 ===")
    mgr = fresh()
    lr = mgr.get_loan_returns()[0]
    count_before = mgr.tottenham_sales_count
    ok, _ = mgr.sell_player(lr.id)
    assert_true(ok, "sell loan return")
    assert_eq(mgr.tottenham_sales_count, count_before, "loan return sale not counted")


def test_u21_exempt():
    print("\n=== U21 exempt from roster and non-HG ===")
    mgr = fresh()
    u21_on_pitch = [p for p in mgr.get_on_pitch() if p.age < 21]
    for p in u21_on_pitch:
        assert_true(not mgr.counts_toward_roster_limit(p), f"{p.name} U21 exempt roster")
        if not p.homegrown:
            assert_true(not mgr.counts_toward_non_hg_limit(p), f"{p.name} U21 exempt non-HG")


def test_remove_from_chart_sidebar():
    print("\n=== Return to sidebar ===")
    mgr = fresh()
    acad_on_pitch = None
    for p in mgr.get_on_pitch():
        if p.origin == "academy":
            acad_on_pitch = p
            break
    if not acad_on_pitch:
        acad = mgr.get_academy()[0]
        mgr.assign_to_chart(acad.id, "ST", 2)
        acad_on_pitch = mgr.players[acad.id]
    pos, slot = acad_on_pitch.depth_pos, acad_on_pitch.depth_slot
    ok, _ = mgr.remove_from_chart(pos, slot)
    assert_true(ok, "return academy to sidebar")
    assert_eq(mgr.players[acad_on_pitch.id].status, "academy", "back to academy status")
    assert_eq(mgr.depth_chart[pos][slot], None, "slot cleared")
    no_duplicates_on_pitch(mgr, "after return to sidebar")


def test_recall_loaned():
    print("\n=== Recall loaned player ===")
    mgr = fresh()
    p = mgr.get_on_pitch()[0]
    pid = p.id
    w0 = mgr.annual_wage_bill_pounds()
    b0 = mgr.budget_m
    mgr.loan_out(pid)
    assert_true(pid not in depth_chart_ids(mgr), "cleared from pitch on loan")
    pos, slot = find_open_slot(mgr)
    ok, msg = mgr.assign_to_chart(pid, pos, slot)
    assert_true(ok, f"recall to {pos}-{('abc')[slot]} ({msg})")
    assert_eq(mgr.budget_m, b0 + 2, "loan credit stays after recall")
    assert_true(mgr.annual_wage_bill_pounds() >= w0, "wages back after recall")


def test_wage_bill_statuses():
    print("\n=== Wage bill statuses ===")
    mgr = fresh()
    for status in WAGE_BILL_STATUSES:
        assert_true(
            any(p.status == status for p in mgr.players.values()),
            f"has player with status {status} for wage test",
        )
    sold = mgr.get_sold()
    if not sold:
        mgr.sell_player("gkc")
    sold_p = [p for p in mgr.players.values() if p.status == "sold"][0]
    loaned = mgr.get_loaned_out()
    if not loaned:
        mgr.loan_out(mgr.get_loan_returns()[0].id)
    loaned_p = [p for p in mgr.players.values() if p.status == "loaned_out"][0]
    assert_true(sold_p.id not in [p.id for p in mgr.players_on_wage_bill()], "sold off wages")
    assert_true(loaned_p.id not in [p.id for p in mgr.players_on_wage_bill()], "loaned off wages")


def test_save_reload():
    print("\n=== Save and reload ===")
    mgr = fresh()
    mgr.sell_player("gka")
    mgr.loan_out(mgr.get_academy()[0].id)
    slug = mgr.team_slug
    budget = mgr.budget_m
    sales = mgr.tottenham_sales_count
    wages = mgr.annual_wage_bill_pounds()
    loaded = SquadManager.load_game(slug)
    assert_true(loaded is not None, "load save")
    assert_eq(loaded.budget_m, budget, "budget persisted")
    assert_eq(loaded.tottenham_sales_count, sales, "sales persisted")
    assert_eq(loaded.annual_wage_bill_pounds(), wages, "wages persisted")
    no_duplicates_on_pitch(loaded, "after reload")


def test_parse_slot_ids():
    print("\n=== CSV slot id parsing ===")
    mgr = fresh()
    cases = [
        ("gka", ("GK", 0)),
        ("rcbb", ("RCB", 1)),
        ("lcma", ("LCM", 0)),
        ("stb", ("ST", 1)),
        ("vicario-1", None),
    ]
    for pid, expected in cases:
        got = mgr._parse_depth_slot_id(pid)
        assert_eq(got, expected, f"parse {pid}")


def test_squad_origin_cannot_return_to_sidebar():
    print("\n=== Squad origin cannot return to sidebar ===")
    mgr = fresh()
    p = mgr.players["gka"]
    ok, msg = mgr.remove_from_chart(p.depth_pos, p.depth_slot)
    assert_true(not ok and "sold or loaned" in msg, "squad player cannot return to sidebar")


def test_budget_negative_allowed_in_play():
    print("\n=== Over-budget buy allowed during play ===")
    mgr = fresh()
    while mgr.get_market():
        p = mgr.get_market()[0]
        try:
            pos, slot = find_open_slot(mgr)
        except RuntimeError:
            break
        mgr.assign_to_chart(p.id, pos, slot)
        if mgr.budget_m < 0:
            break
    assert_true(mgr.budget_m < 0, "budget can go negative during play")
    assert_true(any("OVER BUDGET" in w for w in mgr.get_warnings()), "over budget warning shown")


def test_wage_invariant_across_actions():
    print("\n=== Wage bill invariant across action chain ===")
    mgr = fresh()
    actions = [
        lambda: mgr.sell_player("gkb"),
        lambda: mgr.loan_out(mgr.get_academy()[0].id),
        lambda: mgr.assign_to_chart(
            mgr.get_injured()[0].id, *find_open_slot(mgr)
        ),
    ]
    for act in actions:
        act()
        assert_eq(
            mgr.annual_wage_bill_pounds(),
            manual_wage_bill(mgr),
            "wage bill matches after action",
        )
    no_duplicates_on_pitch(mgr, "after action chain")


def test_loan_credit_not_reversed_on_recall():
    print("\n=== Loan budget credit is not reversed on recall ===")
    mgr = fresh()
    p = mgr.get_on_pitch()[0]
    b0 = mgr.budget_m
    mgr.loan_out(p.id)
    assert_eq(mgr.budget_m, b0 + 2, "loan adds 2M once")
    pos, slot = find_open_slot(mgr)
    mgr.assign_to_chart(p.id, pos, slot)
    assert_eq(mgr.budget_m, b0 + 2, "recall does not remove loan credit")
    mgr.loan_out(p.id)
    assert_eq(mgr.budget_m, b0 + 4, "second loan adds another 2M")


def test_resolve_injured_for_finish():
    print("\n=== Place all injured (finish prerequisite) ===")
    mgr = fresh()
    for inj in list(mgr.get_injured()):
        pos, slot = find_open_slot(mgr)
        ok, _ = mgr.assign_to_chart(inj.id, pos, slot)
        assert_true(ok, f"place injured {inj.name}")
    assert_eq(len(mgr.get_injured()), 0, "no injured left in sidebar")
    no_duplicates_on_pitch(mgr, "all injured placed")


def test_every_player_single_status():
    print("\n=== Each player has exactly one status ===")
    mgr = fresh()
    mgr.sell_player("gkb")
    mgr.loan_out(mgr.get_academy()[0].id)
    for p in mgr.players.values():
        on_chart = p.id in depth_chart_ids(mgr)
        if p.status == "depth_chart":
            assert_true(on_chart, f"{p.name} depth_chart must be on pitch")
        elif on_chart:
            assert_true(False, f"{p.name} on pitch but status {p.status}")


def test_resolve_all_loan_returns():
    print("\n=== Resolve all loan returns (place, sell, or loan) ===")
    mgr = fresh()
    for lr in list(mgr.get_loan_returns()):
        try:
            pos, slot = find_open_slot(mgr)
            ok, _ = mgr.assign_to_chart(lr.id, pos, slot)
            assert_true(ok, f"place loan return {lr.name}")
        except RuntimeError:
            ok, _ = mgr.sell_player(lr.id)
            if not ok:
                ok, _ = mgr.loan_out(lr.id)
            assert_true(ok, f"sell or loan loan return {lr.name} when pitch full")
    assert_eq(len(mgr.get_loan_returns()), 0, "no loan returns in sidebar")
    no_duplicates_on_pitch(mgr, "all loan returns resolved")
    assert_eq(mgr.annual_wage_bill_pounds(), manual_wage_bill(mgr), "wages still consistent")


def test_demote_within_position():
    print("\n=== Demote within position (ST-a to ST-c) ===")
    mgr = fresh()
    ok, _ = mgr.assign_to_chart("sta", "ST", 2)
    assert_true(ok, "move Solanke to ST-c")
    assert_eq(mgr.depth_chart["ST"][0], None, "ST-a cleared")
    assert_eq(mgr.depth_chart["ST"][2], "sta", "now ST-c")
    no_duplicates_on_pitch(mgr, "after demote")


def test_academy_sell_budget_no_sales_count():
    print("\n=== Academy sell adds budget, not sales count ===")
    mgr = fresh()
    acad = mgr.get_academy()[0]
    b0 = mgr.budget_m
    sc0 = mgr.tottenham_sales_count
    ok, _ = mgr.sell_player(acad.id)
    assert_true(ok, "sell academy player from sidebar")
    assert_eq(mgr.budget_m, b0 + acad.sale_price_m, "budget increased")
    assert_eq(mgr.tottenham_sales_count, sc0, "sales count unchanged for academy")


def test_cannot_finish_initially():
    print("\n=== Finish blocked at game start ===")
    mgr = fresh()
    ok, issues = mgr.can_finish()
    assert_true(not ok, "cannot finish fresh game")
    assert_true(any("loan return" in i.lower() for i in issues), "loan returns block finish")
    assert_true(any("injured" in i.lower() for i in issues), "injured block finish")
    assert_true(len(mgr.get_warnings()) >= 2, "warnings shown for unresolved sidebar")


def test_cannot_finish_over_budget():
    print("\n=== Finish blocked when over budget ===")
    mgr = fresh()
    make_finishable_loan_returns_out(mgr)
    assert_true(mgr.can_finish()[0], "finishable before overspend")
    while mgr.get_market() and mgr.budget_m >= 0:
        p = mgr.get_market()[0]
        try:
            pos, slot = find_open_slot(mgr)
        except RuntimeError:
            mgr.sell_player(mgr.get_on_pitch()[-1].id)
            pos, slot = find_open_slot(mgr)
        mgr.assign_to_chart(p.id, pos, slot)
    assert_true(mgr.budget_m < 0, "budget went negative")
    ok, issues = mgr.can_finish()
    assert_true(not ok, "cannot finish over budget")
    assert_true(any("budget" in i.lower() for i in issues), "budget issue listed")
    assert_true(any("OVER BUDGET" in w for w in mgr.get_warnings()), "over budget warning")


def test_cannot_finish_over_roster():
    print("\n=== Finish blocked when over roster limit ===")
    mgr = fresh()
    place_all_injured(mgr)
    place_all_loan_returns(mgr)
    assert_true(mgr.roster_count() > mgr.config["max_squad_size"], "over roster after placing everyone")
    ok, issues = mgr.can_finish()
    assert_true(not ok, "cannot finish over roster")
    assert_true(any("roster" in i.lower() or "25" in i for i in issues), "roster issue listed")
    assert_true(any("OVER ROSTER" in w for w in mgr.get_warnings()), "over roster warning")


def test_cannot_finish_over_non_homegrown():
    print("\n=== Finish blocked when over non-HG limit ===")
    mgr = fresh()
    place_all_injured(mgr)
    place_all_loan_returns(mgr)
    assert_true(mgr.non_homegrown_count() > mgr.config["max_non_homegrown"], "over non-HG after placing everyone")
    ok, issues = mgr.can_finish()
    assert_true(not ok, "cannot finish over non-HG")
    assert_true(any("homegrown" in i.lower() for i in issues), "non-HG issue listed")


def test_finish_success_loan_returns_out():
    print("\n=== Finish success: place injured, loan out returns ===")
    mgr = fresh()
    make_finishable_loan_returns_out(mgr)
    ok, issues = mgr.can_finish()
    assert_true(ok, f"can finish (issues={issues})")
    assert_eq(len(mgr.get_injured()), 0, "no injured in sidebar")
    assert_eq(len(mgr.get_loan_returns()), 0, "no loan returns in sidebar")
    assert_true(mgr.roster_count() <= mgr.config["max_squad_size"], "within roster limit")
    assert_true(mgr.non_homegrown_count() <= mgr.config["max_non_homegrown"], "within non-HG limit")
    assert_true(mgr.budget_m >= 0, "budget non-negative")
    assert_eq(len(mgr.get_warnings()), 0, "no warnings when finishable")
    finish_and_save(mgr)
    assert_true(mgr.completed, "marked complete on save")
    loaded = SquadManager.load_game(mgr.team_slug)
    assert_true(loaded is not None and loaded.completed, "completed flag persists after reload")
    no_duplicates_on_pitch(loaded, "finished squad reload")


def test_finish_success_place_all_then_sell():
    print("\n=== Finish success: place everyone then sell down ===")
    mgr = fresh()
    make_finishable_place_all_then_trim(mgr)
    ok, issues = mgr.can_finish()
    assert_true(ok, f"can finish after trimming (issues={issues})")
    assert_true(len(mgr.get_on_pitch()) > 22, "fuller pitch than starting XI")
    finish_and_save(mgr)
    assert_true(mgr.completed, "marked complete")
    no_duplicates_on_pitch(mgr, "finished after place-all path")


def test_finish_after_buyback_and_recall():
    print("\n=== Finish success after sell, buy back, loan, recall ===")
    mgr = fresh()
    make_finishable_loan_returns_out(mgr)
    assert_true(mgr.can_finish()[0], "finishable before sell/buyback cycle")
    sold = mgr.get_on_pitch()[0]
    pos, slot = sold.depth_pos, sold.depth_slot
    ok, _ = mgr.sell_player(sold.id)
    assert_true(ok, "sell player from pitch")
    assert_true(mgr.can_finish()[0], "still finishable after one sale within limits")
    ok, _ = mgr.assign_to_chart(sold.id, pos, slot)
    assert_true(ok, "buy back sold player")
    assert_true(mgr.can_finish()[0], "finishable again after buy back")
    loaned = mgr.get_on_pitch()[-1]
    mgr.loan_out(loaned.id)
    pos, slot = find_open_slot(mgr)
    ok, _ = mgr.assign_to_chart(loaned.id, pos, slot)
    assert_true(ok, "recall loaned player")
    ok, issues = mgr.can_finish()
    assert_true(ok, f"can finish after recall (issues={issues})")
    finish_and_save(mgr)


def test_finish_starting_xi_populated():
    print("\n=== Finish summary: starting XI uses slot-a players ===")
    mgr = fresh()
    make_finishable_loan_returns_out(mgr)
    ok, _ = mgr.can_finish()
    assert_true(ok, "finishable for XI check")
    for pos in mgr.config["formation"]:
        pid = mgr.depth_chart[pos["key"]][0]
        if pid:
            p = mgr.players[pid]
            assert_eq(p.depth_slot, 0, f"{p.name} in slot-a for {pos['key']}")
    finish_and_save(mgr)


def test_academy_not_required_for_finish():
    print("\n=== Academy players optional for finish ===")
    mgr = fresh()
    make_finishable_loan_returns_out(mgr)
    assert_true(len(mgr.get_academy()) > 0, "academy still in sidebar")
    ok, issues = mgr.can_finish()
    assert_true(ok, f"can finish with academy unresolved (issues={issues})")


def main():
    print("Tottenham Squad Builder — logic tests")
    test_initial_state()
    test_budget_sell_buyback()
    test_budget_loan()
    test_budget_market_buy()
    test_injured_rules()
    test_move_player_no_duplicate()
    test_occupied_slot_blocked()
    test_sales_limit()
    test_loan_return_sell_no_limit()
    test_u21_exempt()
    test_remove_from_chart_sidebar()
    test_recall_loaned()
    test_wage_bill_statuses()
    test_save_reload()
    test_parse_slot_ids()
    test_squad_origin_cannot_return_to_sidebar()
    test_budget_negative_allowed_in_play()
    test_wage_invariant_across_actions()
    test_loan_credit_not_reversed_on_recall()
    test_resolve_injured_for_finish()
    test_every_player_single_status()
    test_resolve_all_loan_returns()
    test_demote_within_position()
    test_academy_sell_budget_no_sales_count()
    test_cannot_finish_initially()
    test_cannot_finish_over_budget()
    test_cannot_finish_over_roster()
    test_cannot_finish_over_non_homegrown()
    test_finish_success_loan_returns_out()
    test_finish_success_place_all_then_sell()
    test_finish_after_buyback_and_recall()
    test_finish_starting_xi_populated()
    test_academy_not_required_for_finish()
    print(f"\n{'=' * 40}")
    print(f"Results: {PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
