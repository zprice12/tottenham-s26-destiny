"""Player data model and helpers."""

from __future__ import annotations

from dataclasses import dataclass

from game.formatting import fmt_m, fmt_pounds_weekly

WEEKS_PER_YEAR = 52


@dataclass
class Player:
    id: str
    name: str
    nationality: str
    position: str
    age: int
    sale_price_m: float
    buy_price_m: float
    contract_years: int
    wages_per_week: int
    homegrown: bool
    origin: str = "squad"
    status: str = "squad"
    depth_pos: str = ""
    depth_slot: int = -1

    @property
    def is_homegrown(self) -> bool:
        return self.homegrown

    @property
    def annual_wage_m(self) -> float:
        return self.wages_per_week * WEEKS_PER_YEAR / 1_000_000

    def short_name(self, max_len: int = 18) -> str:
        if len(self.name) <= max_len:
            return self.name
        parts = self.name.split()
        if len(parts) >= 2:
            short = f"{parts[0][0]}. {parts[-1]}"
            if len(short) <= max_len:
                return short
            if len(parts[-1]) <= max_len:
                return parts[-1]
        return self.name[:max_len]

    def info_line(self, status_label: str = "") -> str:
        hg = "HG" if self.homegrown else "N-HG"
        sale = fmt_m(self.sale_price_m) if self.sale_price_m else "-"
        buy = fmt_m(self.buy_price_m) if self.buy_price_m else "-"
        status = status_label or self.status
        return (
            f"{self.name:<22} {self.position:<4} {self.age:>2}  {self.nationality:<14} "
            f"{hg:<5} Sale {sale:>3}  Buy {buy:>3}  {fmt_pounds_weekly(self.wages_per_week):>12}  "
            f"{self.contract_years:>2}yr  {status}"
        )

    def display_line(self) -> str:
        return self.info_line()


def _wages_per_week_from_row(row: dict) -> int:
    if row.get("wages_per_week"):
        return int(float(row["wages_per_week"]))
    if row.get("wages_m_per_year"):
        return int(float(row["wages_m_per_year"]) * 1_000_000 / WEEKS_PER_YEAR + 0.5)
    return 0


def player_from_row(row: dict, origin: str, status: str) -> Player:
    return Player(
        id=row["id"],
        name=row["name"],
        nationality=row["nationality"],
        position=row["position"].upper(),
        age=int(row["age"]),
        sale_price_m=float(row["sale_price_m"]),
        buy_price_m=float(row["buy_price_m"]),
        contract_years=int(row["contract_years"]),
        wages_per_week=_wages_per_week_from_row(row),
        homegrown=row["homegrown"].strip().lower() in ("yes", "y", "true", "1"),
        origin=origin,
        status=status,
    )
