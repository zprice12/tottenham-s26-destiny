"""Core squad management logic: budget, sales, loans, constraints."""

from __future__ import annotations

from game.config import load_config
from game.data_loader import (
    load_fresh_players,
    players_from_state,
    players_to_state,
)
from game.formatting import fmt_m
from game.player import Player, WEEKS_PER_YEAR
from game.team_saves import load_team, save_team

ROSTER_STATUSES = ("depth_chart", "injured", "loan_return", "academy")
WAGE_BILL_STATUSES = ("depth_chart", "injured", "loan_return", "academy")
SIDEBAR_ORIGINS = ("injured", "loan_return", "academy")


class SquadManager:
    def __init__(self):
        self.config = load_config()
        self.players: dict[str, Player] = {}
        self.budget_m: float = self.config["starting_budget_m"]
        self.tottenham_sales_count: int = 0
        self.depth_chart: dict[str, list[str | None]] = {}
        self.team_name: str = ""
        self.team_slug: str = ""
        self.completed: bool = False
        self.created_at: str = ""
        self.bissouma_option_pending: bool = False
        self._init_depth_chart()

    def _init_depth_chart(self):
        slots = self.config["slots_per_position"]
        for pos in self.config["formation"]:
            self.depth_chart[pos["key"]] = [None] * slots

    @classmethod
    def new_game(cls, name: str, slug: str) -> "SquadManager":
        mgr = cls()
        mgr.team_name = name
        mgr.team_slug = slug
        mgr.players = load_fresh_players()
        mgr.bissouma_option_pending = True
        mgr._auto_assign_initial_squad()
        mgr.save()
        return mgr

    @classmethod
    def load_game(cls, slug: str) -> "SquadManager | None":
        state = load_team(slug)
        if not state:
            return None
        mgr = cls()
        mgr.team_name = state.get("name", slug)
        mgr.team_slug = slug
        mgr.completed = state.get("completed", False)
        mgr.created_at = state.get("created_at", "")
        mgr.players = players_from_state(state["players"])
        mgr.budget_m = state["budget_m"]
        mgr.tottenham_sales_count = state["tottenham_sales_count"]
        mgr.depth_chart = state["depth_chart"]
        mgr.bissouma_option_pending = state.get("bissouma_option_pending", False)
        mgr._migrate_cm_to_cam()
        mgr._migrate_legacy_statuses()
        return mgr

    def _migrate_cm_to_cam(self) -> None:
        if "CM" in self.depth_chart:
            if "CAM" not in self.depth_chart:
                self.depth_chart["CAM"] = self.depth_chart.pop("CM")
            else:
                del self.depth_chart["CM"]
        for p in self.players.values():
            if p.depth_pos == "CM":
                p.depth_pos = "CAM"

    def _migrate_legacy_statuses(self) -> None:
        """Move old 'squad' players onto pitch or back to their sidebar."""
        for p in self.players.values():
            if p.status != "squad":
                continue
            if p.origin in SIDEBAR_ORIGINS:
                p.status = p.origin
            else:
                placed = self._place_in_empty_slot(p)
                if not placed:
                    p.status = "depth_chart"

    def _validate_depth_chart(self) -> None:
        seen: set[str] = set()
        for slots in self.depth_chart.values():
            for pid in slots:
                if not pid:
                    continue
                if pid in seen:
                    raise RuntimeError(f"Duplicate player on depth chart: {pid}")
                seen.add(pid)

    def save(self, mark_completed: bool | None = None):
        if mark_completed is not None:
            self.completed = mark_completed
        self._validate_depth_chart()
        save_team(
            self.team_slug,
            {
                "name": self.team_name,
                "completed": self.completed,
                "budget_m": self.budget_m,
                "tottenham_sales_count": self.tottenham_sales_count,
                "depth_chart": self.depth_chart,
                "players": players_to_state(self.players),
                "created_at": self.created_at,
                "bissouma_option_pending": self.bissouma_option_pending,
            },
        )

    def _place_in_empty_slot(self, player: Player) -> bool:
        pos_key = player.position
        if pos_key not in self.depth_chart:
            for pos in self.config["formation"]:
                if pos["key"] == pos_key:
                    break
            else:
                pos_key = self.config["formation"][0]["key"]
        for slot in range(self.config["slots_per_position"]):
            if self.depth_chart[pos_key][slot] is None:
                self._assign_to_chart(player.id, pos_key, slot)
                return True
        for pos in self.config["formation"]:
            for slot in range(self.config["slots_per_position"]):
                if self.depth_chart[pos["key"]][slot] is None:
                    self._assign_to_chart(player.id, pos["key"], slot)
                    return True
        return False

    def _parse_depth_slot_id(self, player_id: str) -> tuple[str, int] | None:
        """
        Parse squad CSV ids like gka, rcbb, lcma into (position_key, slot_index).
        Format: lowercase position code + slot letter a/b/c.
        """
        pid = player_id.strip().lower()
        if len(pid) < 2 or pid[-1] not in "abc":
            return None
        slot = {"a": 0, "b": 1, "c": 2}[pid[-1]]
        pos_part = pid[:-1]
        valid_keys = [pos["key"] for pos in self.config["formation"]]
        for key in sorted(valid_keys, key=len, reverse=True):
            if pos_part == key.lower():
                return key, slot
        return None

    def _auto_assign_initial_squad(self):
        """Place squad players using their CSV id slot codes (gka, rcbb, etc.)."""
        squad = [p for p in self.players.values() if p.origin == "squad" and p.status == "squad"]

        def _slot_sort_key(player: Player) -> tuple[int, int, str]:
            parsed = self._parse_depth_slot_id(player.id)
            if not parsed:
                return (999, 999, player.id)
            pos_key, slot = parsed
            order = next(
                (pos["order"] for pos in self.config["formation"] if pos["key"] == pos_key),
                999,
            )
            return (order, slot, player.id)

        for p in sorted(squad, key=_slot_sort_key):
            parsed = self._parse_depth_slot_id(p.id)
            if parsed:
                pos_key, slot = parsed
                if pos_key in self.depth_chart and self.depth_chart[pos_key][slot] is None:
                    self._assign_to_chart(p.id, pos_key, slot)
                    continue
            self._place_in_empty_slot(p)

    def _sidebar_status_for_origin(self, origin: str) -> str:
        if origin in SIDEBAR_ORIGINS:
            return origin
        return "loan_return"

    def _assign_to_chart(self, player_id: str, pos_key: str, slot: int):
        p = self.players[player_id]
        self._clear_chart_slot(player_id)
        self.depth_chart[pos_key][slot] = player_id
        p.depth_pos = pos_key
        p.depth_slot = slot
        p.status = "depth_chart"

    def _clear_chart_slot(self, player_id: str):
        for slots in self.depth_chart.values():
            for i, pid in enumerate(slots):
                if pid == player_id:
                    slots[i] = None

    def _remove_from_chart(self, player_id: str) -> tuple[bool, str]:
        p = self.players.get(player_id)
        if not p or p.status != "depth_chart":
            return False, "Player is not on the pitch."
        self._clear_chart_slot(player_id)
        p.depth_pos = ""
        p.depth_slot = -1
        if p.origin in SIDEBAR_ORIGINS:
            p.status = p.origin
            return True, f"{p.name} returned to {p.origin.replace('_', ' ')}."
        return False, f"{p.name} must be sold or loaned out — no bench space."

    def get_on_pitch(self) -> list[Player]:
        return [p for p in self.players.values() if p.status == "depth_chart"]

    def get_loan_returns(self) -> list[Player]:
        return sorted(
            [p for p in self.players.values() if p.status == "loan_return"],
            key=lambda x: x.name,
        )

    def get_injured(self) -> list[Player]:
        return sorted(
            [p for p in self.players.values() if p.status == "injured"],
            key=lambda x: x.name,
        )

    def get_academy(self) -> list[Player]:
        return sorted(
            [p for p in self.players.values() if p.status == "academy"],
            key=lambda x: x.name,
        )

    def get_market(self) -> list[Player]:
        return sorted(
            [p for p in self.players.values() if p.status == "market"],
            key=lambda x: x.name,
        )

    def get_sold(self) -> list[Player]:
        return sorted(
            [p for p in self.players.values() if p.status == "sold"],
            key=lambda x: x.name,
        )

    def get_loaned_out(self) -> list[Player]:
        return sorted(
            [p for p in self.players.values() if p.status == "loaned_out"],
            key=lambda x: x.name,
        )

    def _roster_age_cutoff(self) -> int:
        return self.config.get("roster_u21_exempt_age", 21)

    def _on_current_squad(self, player: Player) -> bool:
        """Player has been placed on the pitch (counts toward squad limits)."""
        return player.status == "depth_chart"

    def counts_toward_roster_limit(self, player: Player) -> bool:
        """On-squad players aged 21+ count toward the 25-man limit."""
        return (
            self._on_current_squad(player)
            and player.age >= self._roster_age_cutoff()
        )

    def counts_toward_non_hg_limit(self, player: Player) -> bool:
        """On-squad non-homegrown players aged 21+ count toward the 17 limit."""
        return (
            self._on_current_squad(player)
            and not player.homegrown
            and player.age >= self._roster_age_cutoff()
        )

    def roster_count(self) -> int:
        """On-squad players counting toward the 25-man limit (U21 exempt)."""
        return sum(1 for p in self.players.values() if self.counts_toward_roster_limit(p))

    def squad_players_on_pitch(self) -> int:
        return len(self.get_on_pitch())

    def u21_exempt_count(self) -> int:
        """On-squad under-21 players (exempt from roster and non-HG limits)."""
        cutoff = self._roster_age_cutoff()
        return sum(
            1 for p in self.players.values()
            if self._on_current_squad(p) and p.age < cutoff
        )

    def u21_non_hg_exempt_count(self) -> int:
        cutoff = self._roster_age_cutoff()
        return sum(
            1 for p in self.players.values()
            if self._on_current_squad(p) and p.age < cutoff and not p.homegrown
        )

    def non_homegrown_count(self) -> int:
        return sum(1 for p in self.players.values() if self.counts_toward_non_hg_limit(p))

    def players_on_wage_bill(self) -> list[Player]:
        """Injured, academy, loan returns, and squad players on the pitch."""
        return [p for p in self.players.values() if p.status in WAGE_BILL_STATUSES]

    def annual_wage_bill_pounds(self) -> int:
        return sum(p.wages_per_week * WEEKS_PER_YEAR for p in self.players_on_wage_bill())

    def total_wages_m(self) -> float:
        return self.annual_wage_bill_pounds() / 1_000_000

    def total_wages_m_rounded(self) -> int:
        return int(self.total_wages_m() + 0.5)

    def _counts_toward_sales_limit(self, player: Player) -> bool:
        return player.origin == "squad"

    def slot_occupied(self, pos_key: str, slot: int, excluding: str | None = None) -> bool:
        pid = self.depth_chart.get(pos_key, [None])[slot]
        if not pid:
            return False
        if excluding and pid == excluding:
            return False
        return True

    def get_slot_player(self, pos_key: str, slot: int) -> Player | None:
        pid = self.depth_chart.get(pos_key, [None, None, None])[slot]
        if pid and pid in self.players:
            return self.players[pid]
        return None

    def get_open_slots(self, pos_key: str) -> list[int]:
        slots = self.config["slots_per_position"]
        return [
            i
            for i in range(slots)
            if not self.depth_chart.get(pos_key, [None] * slots)[i]
        ]

    def can_sell(self, player: Player) -> tuple[bool, str]:
        if player.status == "injured":
            return False, "Injured players must be placed on the pitch — they cannot be sold."
        if player.status not in ROSTER_STATUSES:
            return False, "That player cannot be sold."
        if self._counts_toward_sales_limit(player):
            if self.tottenham_sales_count >= self.config["max_tottenham_sales"]:
                return False, "You have already sold 8 players from the current squad/injured list."
        return True, ""

    def sell_player(self, player_id: str) -> tuple[bool, str]:
        p = self.players.get(player_id)
        if not p:
            return False, "Player not found."
        ok, msg = self.can_sell(p)
        if not ok:
            return False, msg

        if p.status == "depth_chart":
            self._clear_chart_slot(player_id)
            p.depth_pos = ""
            p.depth_slot = -1

        p.status = "sold"
        self.budget_m += p.sale_price_m
        if self._counts_toward_sales_limit(p):
            self.tottenham_sales_count += 1
        self.save()
        return True, f"Sold {p.name} for {fmt_m(p.sale_price_m)}."

    def _loan_budget_credit_m(self, player: Player) -> float:
        if player.origin == "academy":
            return self.config.get("academy_loan_wage_savings_m", 1)
        return self.config["loan_wage_savings_m"]

    def loan_out(self, player_id: str) -> tuple[bool, str]:
        p = self.players.get(player_id)
        if not p:
            return False, "Player not found."
        if p.status == "injured":
            return False, "Injured players must be placed on the pitch — they cannot be loaned out."
        if p.status not in ROSTER_STATUSES:
            return False, "That player cannot be loaned out."

        if p.status == "depth_chart":
            self._clear_chart_slot(player_id)
            p.depth_pos = ""
            p.depth_slot = -1

        p.status = "loaned_out"
        credit = self._loan_budget_credit_m(p)
        self.budget_m += credit
        self.save()
        return True, (
            f"Loaned out {p.name}. +{fmt_m(credit)} added to budget. Wages off the books."
        )

    def assign_to_chart(self, player_id: str, pos_key: str, slot: int) -> tuple[bool, str]:
        p = self.players.get(player_id)
        if not p:
            return False, "Player not found."

        valid_keys = [pos["key"] for pos in self.config["formation"]]
        if pos_key not in valid_keys:
            return False, f"Invalid position: {pos_key}"
        if slot < 0 or slot >= self.config["slots_per_position"]:
            return False, "Invalid slot."

        allowed = ROSTER_STATUSES + ("sold", "loaned_out", "market")
        if p.status not in allowed:
            return False, "That player cannot be placed on the pitch."

        existing = self.depth_chart[pos_key][slot]
        if existing and existing != player_id:
            other = self.players[existing].name
            return False, (
                f"{pos_key}-{('abc')[slot]} is occupied by {other}. "
                "Move them first or pick an empty slot."
            )

        if p.status == "market":
            self.budget_m -= p.buy_price_m

        elif p.status == "sold":
            self.budget_m -= p.sale_price_m
            if self._counts_toward_sales_limit(p):
                self.tottenham_sales_count = max(0, self.tottenham_sales_count - 1)

        elif p.status in ("loaned_out", "injured", "loan_return", "academy", "depth_chart"):
            pass

        self._assign_to_chart(player_id, pos_key, slot)
        self.save()
        letters = "abc"
        return True, f"Placed {p.name} at {pos_key}-{letters[slot]}."

    def remove_from_chart(self, pos_key: str, slot: int) -> tuple[bool, str]:
        pid = self.depth_chart[pos_key][slot]
        if not pid:
            return False, "That slot is empty."
        return self._remove_from_chart(pid)

    def promote_on_chart(self, player_id: str) -> tuple[bool, str]:
        """Move player up the depth chart (toward slot a), swapping with occupant above."""
        p = self.players.get(player_id)
        if not p or p.status != "depth_chart":
            return False, "Player is not on the pitch."
        pos_key = p.depth_pos
        slot = p.depth_slot
        if slot <= 0:
            return False, "Already at slot a — cannot promote further."
        new_slot = slot - 1
        letters = "abc"
        other_id = self.depth_chart[pos_key][new_slot]
        if other_id:
            other = self.players[other_id]
            self.depth_chart[pos_key][slot] = other_id
            self.depth_chart[pos_key][new_slot] = player_id
            other.depth_slot = slot
            p.depth_slot = new_slot
            self.save()
            return True, (
                f"Promoted {p.name} to {pos_key}-{letters[new_slot]} "
                f"(swapped with {other.name})."
            )
        self.depth_chart[pos_key][slot] = None
        self.depth_chart[pos_key][new_slot] = player_id
        p.depth_slot = new_slot
        self.save()
        return True, f"Promoted {p.name} to {pos_key}-{letters[new_slot]}."

    def demote_on_chart(self, player_id: str) -> tuple[bool, str]:
        """Move player down the depth chart (toward slot c), swapping with occupant below."""
        p = self.players.get(player_id)
        if not p or p.status != "depth_chart":
            return False, "Player is not on the pitch."
        pos_key = p.depth_pos
        slot = p.depth_slot
        max_slot = self.config["slots_per_position"] - 1
        if slot >= max_slot:
            return False, "Already at slot c — cannot demote further."
        new_slot = slot + 1
        letters = "abc"
        other_id = self.depth_chart[pos_key][new_slot]
        if other_id:
            other = self.players[other_id]
            self.depth_chart[pos_key][slot] = other_id
            self.depth_chart[pos_key][new_slot] = player_id
            other.depth_slot = slot
            p.depth_slot = new_slot
            self.save()
            return True, (
                f"Demoted {p.name} to {pos_key}-{letters[new_slot]} "
                f"(swapped with {other.name})."
            )
        self.depth_chart[pos_key][slot] = None
        self.depth_chart[pos_key][new_slot] = player_id
        p.depth_slot = new_slot
        self.save()
        return True, f"Demoted {p.name} to {pos_key}-{letters[new_slot]}."

    def get_warnings(self) -> list[str]:
        warnings = []
        if self.budget_m < 0:
            warnings.append(f"OVER BUDGET — {fmt_m(self.budget_m)} remaining (sell players or undo buys)")
        if self.roster_count() > self.config["max_squad_size"]:
            max_sz = self.config["max_squad_size"]
            u21 = self.u21_exempt_count()
            extra = f" ({u21} U21 exempt)" if u21 else ""
            warnings.append(
                f"OVER ROSTER — {self.roster_count()}/{max_sz} counting toward limit{extra}; "
                "sell or loan someone out"
            )
        if self.non_homegrown_count() > self.config["max_non_homegrown"]:
            max_nhg = self.config["max_non_homegrown"]
            u21_nhg = self.u21_non_hg_exempt_count()
            extra = f" ({u21_nhg} U21 exempt)" if u21_nhg else ""
            warnings.append(
                f"OVER NON-HOMEGROWN — {self.non_homegrown_count()}/{max_nhg} on squad{extra}"
            )
        n_lr = len(self.get_loan_returns())
        if n_lr:
            warnings.append(
                f"{n_lr} LOAN RETURN{'S' if n_lr != 1 else ''} — place on pitch, sell, or loan out"
            )
        n_inj = len(self.get_injured())
        if n_inj:
            warnings.append(
                f"{n_inj} INJURED PLAYER{'S' if n_inj != 1 else ''} — place on pitch (cannot sell or loan)"
            )
        return warnings

    def can_finish(self) -> tuple[bool, list[str]]:
        issues = []
        if self.budget_m < 0:
            issues.append("Budget is negative. Sell players or undo buys.")
        if self.roster_count() > self.config["max_squad_size"]:
            u21 = self.u21_exempt_count()
            extra = f" ({u21} under-21 exempt)" if u21 else ""
            issues.append(
                f"Roster has {self.roster_count()} players counting toward the limit "
                f"(max 25){extra}."
            )
        if self.non_homegrown_count() > self.config["max_non_homegrown"]:
            issues.append(
                f"Too many non-homegrown on squad ({self.non_homegrown_count()}/17 counting)."
            )
        if self.get_loan_returns():
            issues.append("Resolve all loan returns (sell, loan, or place on pitch).")
        if self.get_injured():
            issues.append("Place all injured players on the pitch (they cannot be sold or loaned).")
        return len(issues) == 0, issues

    def add_bissouma(self) -> tuple[bool, str]:
        """Keep Yves Bissouma on his one-year contract option."""
        if "bissouma-1" in self.players:
            return False, "Bissouma is already on the squad."

        p = Player(
            id="bissouma-1",
            name="Yves Bissouma",
            nationality="Mali",
            position="RCM",
            age=29,
            sale_price_m=0,
            buy_price_m=0,
            contract_years=1,
            wages_per_week=60000,
            homegrown=False,
            origin="squad",
            status="squad",
        )
        self.players[p.id] = p

        for slot in range(self.config["slots_per_position"]):
            if not self.depth_chart["RCM"][slot]:
                return self.assign_to_chart(p.id, "RCM", slot)

        p.status = "loan_return"
        p.origin = "loan_return"
        self.save()
        return True, (
            "Yves Bissouma kept on his one-year option (£60k/wk). "
            "RCM is full — place him from the pick menu when you have a slot."
        )

    def get_manageable_players(self) -> list[dict]:
        entries: list[dict] = []
        for p in self.get_injured():
            entries.append({"player": p, "label": "injured"})
        for p in self.get_loan_returns():
            entries.append({"player": p, "label": "loan return"})
        for p in self.get_academy():
            entries.append({"player": p, "label": "academy"})
        for p in self.get_on_pitch():
            slot = "abc"[p.depth_slot]
            entries.append({"player": p, "label": f"pitch {p.depth_pos}-{slot}"})
        for p in self.get_sold():
            entries.append({"player": p, "label": f"sold — buy back {fmt_m(p.sale_price_m)}"})
        for p in self.get_loaned_out():
            entries.append({"player": p, "label": "loaned out — recall"})
        return entries

    def get_directory_players(self) -> list[tuple[Player, str]]:
        """All club players (not transfer market) with a readable status label."""
        entries: list[tuple[Player, str]] = []
        for p in self.get_on_pitch():
            slot = "abc"[p.depth_slot]
            entries.append((p, f"Pitch {p.depth_pos}-{slot}"))
        for p in self.get_injured():
            entries.append((p, "Injured"))
        for p in self.get_loan_returns():
            entries.append((p, "Loan return"))
        for p in self.get_academy():
            entries.append((p, "Academy"))
        for p in self.get_sold():
            entries.append((p, "Sold"))
        for p in self.get_loaned_out():
            entries.append((p, "Loaned out"))
        return sorted(entries, key=lambda x: (x[1], x[0].name))
