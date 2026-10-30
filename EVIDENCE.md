# Evidence

## Automated local checks
Not yet run in the target environment. After installing requirements, run `python -m unittest discover -s tests -v` and paste the exact terminal output here.

## Acceptance probes
| Requirement | Evidence status |
|---|---|
| Same idempotency key creates one usage event | Unit test included; runtime output not yet recorded |
| Exact quota boundary and next request returns 429 | Unit test included; runtime output not yet recorded |
| Stripe Checkout changes Free to Pro via webhook | Not yet run; requires Stripe test credentials and Stripe CLI |
| Forged signature returns 400; duplicate event ignored | Handler implemented; not yet exercised |
| Cached-input and reasoning-token pricing | Arithmetic unit test included; pricing rates are illustrative |
| Monthly usage rollup | `/usage/{tenant_id}` endpoint implemented; not yet recorded |

Do not mark an item passed until the actual command/API transcript is pasted here.
