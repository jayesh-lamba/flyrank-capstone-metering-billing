# Usage Metering & Billing Engine

A small multi-tenant backend that meters API calls and simulated AI tokens, enforces monthly quotas, calculates token costs using integer micro-USD, and synchronizes subscription state from verified Stripe test-mode webhooks.

## Architecture

```text
Client -> FastAPI route -> Billing service -> SQLite
                         | idempotency key + unique constraint
                         | quota check before event insert
                         v
                    usage_events -> monthly rollup -> /usage
Client -> /billing/checkout -> Stripe Checkout (test mode)
Stripe -> signed webhook -> signature verification -> event dedupe -> tenant plan sync
```

## Plans

| Plan | API calls/month | AI tokens/month |
|---|---:|---:|
| Free | 1,000 | 100,000 |
| Pro | 100,000 | 10,000,000 |

## Setup (Python 3.11+)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python scripts/seed.py
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs.

## Demo

Create a tenant:
```powershell
Invoke-RestMethod -Method Post http://127.0.0.1:8000/tenants -ContentType 'application/json' -Body '{"id":"acme","name":"Acme"}'
```
Record usage with an idempotency key:
```powershell
Invoke-RestMethod -Method Post http://127.0.0.1:8000/usage/record -ContentType 'application/json' -Body '{"tenant_id":"acme","usage_type":"api_calls","quantity":1,"idempotency_key":"req-001"}'
```
Read monthly usage:
```powershell
Invoke-RestMethod http://127.0.0.1:8000/usage/acme
```

## Stripe test mode

Create a Stripe test-mode Product and recurring Price, then place `sk_test_...`, the Price ID and webhook secret in `.env`. Run:
```bash
stripe listen --forward-to localhost:8000/webhooks/stripe
```
Copy the CLI's `whsec_...` into `.env`, restart the server, and configure the test checkout. Use only Stripe test mode. No real payment is made. Without these credentials, checkout returns 503 and webhooks cannot be exercised.

## Cost model

Pricing constants are pinned in `app/config.py` as illustrative integer micro-USD per million tokens. Cached input is a subset of input, so it is subtracted from fresh input before applying the lower cached rate. Reasoning tokens are a subset of output and are not added a second time. Replace the illustrative rates with the exact provider/model rates selected for your evaluation and document that choice.

## Tests

```powershell
python -m unittest discover -s tests -v
```

## Limitations

This starter uses SQLite and synchronous request handling for a compact local demo. The background-job requirement in the shared evaluation rubric is not yet implemented as a separate worker; add a retryable reconciliation/rollup job before claiming that requirement. Stripe Checkout and webhook code require real test-mode credentials and have not been exercised in this repository package. No live Stripe success is claimed. The pricing values are illustrative and must be confirmed against the provider/model selected by the evaluator. The test suite covers idempotency, quota boundary and arithmetic only; tenant isolation and Stripe replay/forgery probes should be added and run before submission.
