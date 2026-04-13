"""Currency conversion utilities."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

EXCHANGE_RATES: dict[str, Decimal] = {
    "USD": Decimal("1.00"),
    "EUR": Decimal("0.92"),
    "GBP": Decimal("0.79"),
    "JPY": Decimal("149.50"),
    "CAD": Decimal("1.36"),
}


def convert_currency(
    amount: Decimal,
    from_currency: str,
    to_currency: str,
) -> Decimal:
    """Convert amount between currencies using stored rates."""
    if from_currency not in EXCHANGE_RATES:
        raise ValueError(f"Unsupported currency: {from_currency}")
    if to_currency not in EXCHANGE_RATES:
        raise ValueError(f"Unsupported currency: {to_currency}")

    usd_amount = amount / EXCHANGE_RATES[from_currency]
    converted = usd_amount * EXCHANGE_RATES[to_currency]
    return converted.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
