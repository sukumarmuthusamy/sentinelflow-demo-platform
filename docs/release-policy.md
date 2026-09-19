# Release Policy (Synthetic)

Policy thresholds mirrored from SentinelFlow domain packs for eval ground truth.

## Verdict thresholds

| Signal | Threshold | Verdict |
|--------|-----------|---------|
| oasdiff ERR on critical service | any | BLOCK |
| gitleaks verified secret | any | BLOCK |
| evidence coverage | < 0.75 | REVIEW |
| blast radius with inadequate tests | high + low coverage | REVIEW |
| documentation-only change | minimal radius | PASS |

## Critical services

- `svc-core-api` (healthcare-claims)
- `svc-payment-api` (ecommerce-payments)
