# PayFlow API

Internal payment processing service for Acme Corp. Handles billing, invoicing, refunds, and promotion management.

## Stack
- Python 3.12
- FastAPI
- PostgreSQL
- Stripe SDK

## Quick Start
```bash
pip install -r requirements.txt
uvicorn src.api.main:app --reload
```

## Architecture
- `src/billing/` — Core billing engine, invoicing, refunds, currency
- `src/auth/` — Role-based authorization and permission checks
- `src/api/` — FastAPI route handlers
