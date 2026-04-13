"""Refund processing for PayFlow API."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class Refund:
    refund_id: str
    invoice_id: str
    amount: Decimal
    reason: str
    status: str = "pending"
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


def process_refund(
    refund_id: str,
    invoice_id: str,
    original_total: Decimal,
    refund_amount: Decimal,
    reason: str = "",
) -> Refund:
    """Process a refund, validating against the original invoice total."""
    if refund_amount <= 0:
        raise ValueError("Refund amount must be positive")
    if refund_amount > original_total:
        raise ValueError("Refund cannot exceed original invoice total")
    return Refund(
        refund_id=refund_id,
        invoice_id=invoice_id,
        amount=refund_amount,
        reason=reason,
        status="approved",
    )
