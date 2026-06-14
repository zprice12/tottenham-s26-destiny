"""Load CSV player databases and persist runtime state."""

from __future__ import annotations

import csv
from pathlib import Path

from game.player import Player, WEEKS_PER_YEAR, player_from_row

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"

CSV_SOURCES = {
    "squad": ("squad.csv", "squad", "squad"),
    "loan_return": ("loan_returns.csv", "loan_return", "loan_return"),
    "injured": ("injured.csv", "injured", "injured"),
    "academy": ("academy.csv", "academy", "academy"),
    "market": ("transfer_market.csv", "market", "market"),
}


def _read_csv(filename: str) -> list[dict]:
    path = DATA_DIR / filename
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_fresh_players() -> dict[str, Player]:
    players: dict[str, Player] = {}
    for _key, (filename, origin, status) in CSV_SOURCES.items():
        for row in _read_csv(filename):
            p = player_from_row(row, origin=origin, status=status)
            players[p.id] = p
    return players


def players_to_state(players: dict[str, Player]) -> list[dict]:
    result = []
    for p in players.values():
        result.append(
            {
                "id": p.id,
                "name": p.name,
                "nationality": p.nationality,
                "position": p.position,
                "age": p.age,
                "sale_price_m": p.sale_price_m,
                "buy_price_m": p.buy_price_m,
                "contract_years": p.contract_years,
                "wages_per_week": p.wages_per_week,
                "homegrown": p.homegrown,
                "origin": p.origin,
                "status": p.status,
                "depth_pos": p.depth_pos,
                "depth_slot": p.depth_slot,
            }
        )
    return result


def players_from_state(data: list[dict]) -> dict[str, Player]:
    players: dict[str, Player] = {}
    for row in data:
        wages_per_week = row.get("wages_per_week")
        if wages_per_week is None and row.get("wages_m_per_year") is not None:
            wages_per_week = int(
                float(row["wages_m_per_year"]) * 1_000_000 / WEEKS_PER_YEAR + 0.5
            )
        p = Player(
            id=row["id"],
            name=row["name"],
            nationality=row["nationality"],
            position=row["position"],
            age=row["age"],
            sale_price_m=row["sale_price_m"],
            buy_price_m=row["buy_price_m"],
            contract_years=row["contract_years"],
            wages_per_week=int(wages_per_week or 0),
            homegrown=row["homegrown"],
            origin=row["origin"],
            status=row["status"],
            depth_pos=row.get("depth_pos", ""),
            depth_slot=row.get("depth_slot", -1),
        )
        players[p.id] = p
    return players
