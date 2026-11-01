"""Conservative local budget guard for API calls."""

import os
from datetime import datetime, timezone

from .task_manager import month_spend_usd

# Default is intentionally below R$30 to leave room for FX, taxes and price changes.
DEFAULT_MONTHLY_BUDGET_USD = 4.50


def monthly_budget_usd() -> float:
    try:
        value = float(os.getenv("JARVIS_MONTHLY_BUDGET_USD", str(DEFAULT_MONTHLY_BUDGET_USD)))
    except ValueError:
        value = DEFAULT_MONTHLY_BUDGET_USD
    return max(0.0, value)


def input_price_per_million() -> float:
    return max(0.0, float(os.getenv("JARVIS_INPUT_PRICE_PER_MILLION", "0.75")))


def output_price_per_million() -> float:
    return max(0.0, float(os.getenv("JARVIS_OUTPUT_PRICE_PER_MILLION", "4.50")))


def estimate_call_cost_usd(input_tokens: int, output_tokens: int) -> float:
    return (
        max(0, input_tokens) * input_price_per_million()
        + max(0, output_tokens) * output_price_per_million()
    ) / 1_000_000


def can_afford_estimate(input_tokens: int, output_tokens: int) -> bool:
    return month_spend_usd() + estimate_call_cost_usd(input_tokens, output_tokens) <= monthly_budget_usd()


def budget_status() -> dict[str, float | str]:
    budget = monthly_budget_usd()
    spent = month_spend_usd()
    return {
        "month_utc": datetime.now(timezone.utc).strftime("%Y-%m"),
        "budget_usd": round(budget, 4),
        "tracked_spend_usd": round(spent, 6),
        "remaining_usd": round(max(0.0, budget - spent), 6),
        "warning": "Estimativa local; confira o painel da API. Limites da plataforma podem ter atraso.",
    }
