"""Dynamic pricing and promotion engine for PayFlow API.

Supports percentage discounts, stackable promo codes, loyalty tiers,
bulk pricing, and bill splitting with tips.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional


@dataclass
class Promotion:
    promo_id: str
    name: str
    discount_percent: Decimal
    min_order_amount: Decimal = Decimal("0.00")
    max_uses: int = -1
    uses: int = 0
    expires_at: Optional[datetime] = None
    stackable: bool = False


_active_promotions: dict[str, Promotion] = {}


def register_promotion(promo: Promotion) -> None:
    """Register a promotion in the active promotions registry."""
    _active_promotions[promo.promo_id] = promo


def apply_discount(
    subtotal: Decimal,
    discount_percent: Decimal,
) -> Decimal:
    """Apply a percentage discount to a subtotal and return the final price."""
    discount = subtotal * discount_percent / Decimal("100")
    return (subtotal - discount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def apply_stacked_discounts(
    subtotal: Decimal,
    promo_codes: list[str],
) -> Decimal:
    """Apply multiple promotional discounts sequentially."""
    current = subtotal
    for code in promo_codes:
        promo = _active_promotions.get(code)
        if promo is None:
            continue
        current = apply_discount(current, promo.discount_percent)
        promo.uses += 1
    return current


def calculate_loyalty_discount(
    total_spent_lifetime: Decimal,
    current_order: Decimal,
) -> Decimal:
    """Calculate loyalty tier discount based on customer lifetime spend."""
    if total_spent_lifetime > 10000:
        tier_discount = Decimal("15")
    elif total_spent_lifetime > 5000:
        tier_discount = Decimal("10")
    elif total_spent_lifetime > 1000:
        tier_discount = Decimal("5")
    else:
        tier_discount = Decimal("0")

    return apply_discount(current_order, tier_discount)


def format_discount_display(discount_percent: Decimal) -> str:
    """Format a discount percentage for customer-facing display."""
    if not discount_percent:
        return ""
    return f"{discount_percent}% off"


def calculate_bulk_price(
    unit_price: Decimal,
    quantity: int,
    bulk_threshold: int = 10,
    bulk_discount_percent: Decimal = Decimal("15"),
) -> Decimal:
    """Calculate total price with bulk discount when quantity exceeds threshold."""
    total = unit_price * quantity
    if quantity >= bulk_threshold:
        total = apply_discount(total, bulk_discount_percent)
    return total


def split_bill_with_tip(
    subtotal: Decimal,
    tip_percent: Decimal,
    num_people: int,
) -> dict:
    """Split a restaurant-style bill including tip among a group."""
    tip = (subtotal * tip_percent / Decimal("100")).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    total = subtotal + tip
    per_person = (total / num_people).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    return {
        "subtotal": subtotal,
        "tip": tip,
        "total": total,
        "per_person": per_person,
        "num_people": num_people,
    }
