"""Authorization and permission checks."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Role(Enum):
    VIEWER = "viewer"
    BILLING_AGENT = "billing_agent"
    ADMIN = "admin"


ROLE_HIERARCHY = {
    Role.VIEWER: 0,
    Role.BILLING_AGENT: 1,
    Role.ADMIN: 2,
}


@dataclass
class User:
    user_id: str
    role: Role
    org_id: str


def can_issue_refund(user: User, refund_amount: float) -> bool:
    """Check if user has permission to issue a refund of given amount."""
    if user.role == Role.VIEWER:
        return False
    if user.role == Role.BILLING_AGENT and refund_amount > 500.0:
        return False
    return True


def can_access_invoice(user: User, invoice_org_id: str) -> bool:
    """Check if user can access an invoice based on org membership."""
    if user.role == Role.ADMIN:
        return True
    return user.org_id == invoice_org_id
