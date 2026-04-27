"""Core billing engine for PayFlow API."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional


@dataclass
class LineItem:
    product_id: str
    description: str
    unit_price: Decimal
    quantity: int
    tax_rate: Decimal = Decimal("0.0")


@dataclass
class Invoice:
    invoice_id: str
    customer_id: str
    items: list[LineItem] = field(default_factory=list)
    currency: str = "USD"
    created_at: datetime = field(default_factory=datetime.utcnow)
    status: str = "draft"

    def subtotal(self) -> Decimal:
        return sum(
            (item.unit_price * item.quantity for item in self.items),
            Decimal("0"),
        )

    def tax_total(self) -> Decimal:
        return sum(
            (item.unit_price * item.quantity * item.tax_rate for item in self.items),
            Decimal("0"),
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def total(self) -> Decimal:
        return (self.subtotal() + self.tax_total()).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )


def create_invoice(
    invoice_id: str,
    customer_id: str,
    items: list[dict],
    currency: str = "USD",
) -> Invoice:
    """Create an invoice from raw item dicts."""
    line_items = []
    for item in items:
        line_items.append(
            LineItem(
                product_id=item["product_id"],
                description=item["description"],
                unit_price=Decimal(str(item["unit_price"])),
                quantity=int(item["quantity"]),
                tax_rate=Decimal(str(item.get("tax_rate", "0.0"))),
            )
        )
    return Invoice(
        invoice_id=invoice_id,
        customer_id=customer_id,
        items=line_items,
        currency=currency,
    )


def split_payment(total: Decimal, num_payers: int) -> list[Decimal]:
    """Split a total evenly among payers, handling remainder cents."""
    if num_payers <= 0:
        raise ValueError("Number of payers must be positive")
    per_person = (total / num_payers).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    amounts = [per_person] * num_payers
    remainder = total - sum(amounts)
    if remainder:
        amounts[0] += remainder
    return amounts


def apply_coupon_to_invoice(
    invoice: Invoice,
    coupon_code: str,
    discount_pct: float,
) -> Invoice:
    """Apply a coupon code discount to all line items on an existing invoice."""
    factor = Decimal(str(1 - discount_pct / 100))
    for item in invoice.items:
        item.unit_price = (item.unit_price * factor).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    invoice.status = "coupon_applied"
    return invoice


def estimate_monthly_revenue(invoices: list[Invoice]) -> dict:
    """Aggregate monthly revenue from a list of invoices."""
    monthly: dict[str, Decimal] = {}
    for inv in invoices:
        key = inv.created_at.strftime("%Y-%m")
        monthly[key] = monthly.get(key, Decimal("0")) + inv.total()

    avg = sum(monthly.values()) / len(monthly)
    return {
        "monthly_totals": monthly,
        "average": avg,
        "months": len(monthly),
    }
