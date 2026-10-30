# Build Log

AI assistance was used to draft the FastAPI route layer, SQLite schema, metering service, idempotency handling, quota checks, integer token-cost calculation, Stripe Checkout/webhook adapter, tests and documentation.

Human review still required:
- Verify all business rules and explain the idempotency transaction/unique constraint.
- Confirm provider-specific token prices; current constants are explicitly illustrative.
- Run the tests and paste observed output into EVIDENCE.md.
- Configure Stripe test-mode credentials and exercise Checkout, forged signatures and webhook replay.
- Add and test a retryable background worker/reconciliation job to satisfy the shared rubric.
- Review tenant isolation and concurrency behavior before production use.

No real payment credentials or test results are included.
