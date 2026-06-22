"""Display formatting for money and wages."""

from __future__ import annotations


def fmt_m(millions: float) -> str:
    """Millions of pounds, rounded to whole millions."""
    if millions <= 0:
        return "£0M"
    return f"£{int(millions + 0.5)}M"


def fmt_pounds_weekly(amount: int) -> str:
    return f"£{amount:,}/wk"
